from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
from .models import Shipment, ShipmentFee, ShipmentHistory, PaymentTransaction
from .services.finance import FinanceService
import json
from datetime import timedelta

def landing_page(request):
    """Premium enterprise landing page with enhanced design"""
    recent_updates = ShipmentHistory.objects.select_related('shipment').order_by('-timestamp')[:10]
    total_shipments = Shipment.objects.count()
    total_delivered = Shipment.objects.filter(status='delivered').count()
    
    context = {
        'recent_updates': recent_updates,
        'total_shipments': total_shipments,
        'total_delivered': total_delivered,
        'on_time_percentage': 99.8,
        'customer_count': 50000,
    }
    return render(request, 'logistics/landing_enhanced.html', context)


def track_shipment(request):
    """Tracking page - validates ID and shows timeline"""
    tracking_id = request.GET.get('tracking_id', '')
    shipment = None
    error = None
    
    if tracking_id:
        try:
            shipment = Shipment.objects.prefetch_related('fees', 'history').get(tracking_id=tracking_id)
        except Shipment.DoesNotExist:
            error = "Tracking number not found. Please verify and try again."
    
    context = {
        'tracking_id': tracking_id,
        'shipment': shipment,
        'error': error,
    }
    return render(request, 'logistics/tracking.html', context)


def payment_gateway(request, tracking_id):
    """Fee processing gateway with countdown timer"""
    shipment = get_object_or_404(Shipment, tracking_id=tracking_id)
    
    if not shipment.fee_required:
        return redirect('tracking_confirmation', tracking_id=tracking_id)
    
    fees = shipment.fees.all()
    total_fee = sum(fee.amount for fee in fees)
    
    context = {
        'shipment': shipment,
        'fees': fees,
        'total_fee': total_fee,
        'countdown_seconds': 300,
    }
    return render(request, 'logistics/payment.html', context)


def process_payment(request, tracking_id):
    """Process simulated payment transaction with idempotency protection"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    shipment = get_object_or_404(Shipment, tracking_id=tracking_id)
    
    try:
        data = json.loads(request.body)
        cardholder_name = data.get('cardholder_name')
        card_number = data.get('card_number', '')
        expiry_date = data.get('expiry_date')
        cvv = data.get('cvv')
        
        success, transaction, error = FinanceService.process_payment(
            shipment=shipment,
            cardholder_name=cardholder_name,
            card_number=card_number,
            expiry_date=expiry_date,
            cvv=cvv
        )
        
        if success:
            return JsonResponse({
                'success': True,
                'transaction_id': transaction.transaction_id,
                'amount': str(transaction.amount),
                'redirect_url': f'/tracking/{tracking_id}/confirmation/'
            })
        else:
            return JsonResponse({'error': error}, status=400)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def tracking_confirmation(request, tracking_id):
    """Success confirmation page"""
    shipment = get_object_or_404(Shipment, tracking_id=tracking_id)
    latest_payment = shipment.payments.filter(status='completed').first()
    
    context = {
        'shipment': shipment,
        'payment': latest_payment,
    }
    return render(request, 'logistics/confirmation.html', context)


def admin_console(request):
    """Hidden admin console for shipment management"""
    if request.method == 'GET':
        shipments = Shipment.objects.prefetch_related('fees', 'history').all().order_by('-created_at')
        
        total_shipments = shipments.count()
        active_shipments = shipments.exclude(status='delivered').count()
        fee_required_count = shipments.filter(fee_required=True).count()
        delivered_count = shipments.filter(status='delivered').count()
        
        context = {
            'shipments': shipments,
            'total_shipments': total_shipments,
            'active_shipments': active_shipments,
            'fee_required_count': fee_required_count,
            'delivered_count': delivered_count,
        }
        return render(request, 'logistics/admin_console.html', context)
    
    elif request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_shipment':
            tracking_id = Shipment.generate_tracking_id()
            
            fee_amount_raw = request.POST.get('fee_amount', '0')
            try:
                fee_amount_str = str(fee_amount_raw).strip() if fee_amount_raw else '0'
                if not fee_amount_str:
                    fee_amount_str = '0'
                fee_amount = Decimal(fee_amount_str)
                if fee_amount < 0:
                    return JsonResponse({'error': 'Fee amount cannot be negative'}, status=400)
            except (ValueError, TypeError, InvalidOperation):
                return JsonResponse({'error': 'Invalid fee amount format'}, status=400)
            
            shipment = Shipment(
                tracking_id=tracking_id,
                owner_name=request.POST.get('owner_name'),
                owner_email=request.POST.get('owner_email'),
                owner_phone=request.POST.get('owner_phone'),
                owner_address=request.POST.get('owner_address'),
                status='label_created',
                current_location=request.POST.get('current_location', 'Processing Center'),
                destination=request.POST.get('destination'),
                fee_required=request.POST.get('fee_required') == 'on',
                fee_amount=fee_amount,
            )
            
            try:
                shipment.full_clean()
                shipment.save()
            except ValidationError as e:
                return JsonResponse({'error': str(e)}, status=400)
            
            ShipmentHistory.objects.create(
                shipment=shipment,
                status='label_created',
                location=shipment.current_location,
                description='Shipment label created'
            )
            
            if shipment.fee_required and fee_amount > 0:
                fee = ShipmentFee(
                    shipment=shipment,
                    name='Import Duty',
                    amount=fee_amount,
                    description='Import processing fee'
                )
                try:
                    fee.full_clean()
                    fee.save()
                except ValidationError as e:
                    return JsonResponse({'error': f'Invalid fee: {str(e)}'}, status=400)
            
            return redirect('admin_console')
        
        elif action == 'update_shipment':
            shipment_id = request.POST.get('shipment_id')
            shipment = get_object_or_404(Shipment, id=shipment_id)
            
            new_status = request.POST.get('status')
            new_location = request.POST.get('current_location')
            
            if new_status and new_status != shipment.status:
                shipment.status = new_status
                ShipmentHistory.objects.create(
                    shipment=shipment,
                    status=new_status,
                    location=new_location,
                    description=f'Status updated to {shipment.get_status_display()}'
                )
            
            shipment.current_location = new_location
            shipment.fee_required = request.POST.get('fee_required') == 'on'
            
            fee_amount = request.POST.get('fee_amount', shipment.fee_amount)
            try:
                fee_amount_str = str(fee_amount).strip() if fee_amount else str(shipment.fee_amount)
                fee_amount = Decimal(fee_amount_str) if fee_amount_str else shipment.fee_amount
                if fee_amount < 0:
                    return JsonResponse({'error': 'Fee amount cannot be negative'}, status=400)
                shipment.fee_amount = fee_amount
            except (ValueError, TypeError, InvalidOperation):
                return JsonResponse({'error': 'Invalid fee amount'}, status=400)
            
            try:
                shipment.full_clean()
                shipment.save()
            except ValidationError as e:
                return JsonResponse({'error': str(e)}, status=400)
            
            return redirect('admin_console')
        
        elif action == 'add_fee':
            shipment_id = request.POST.get('shipment_id')
            shipment = get_object_or_404(Shipment, id=shipment_id)
            
            fee_amount = request.POST.get('fee_amount', 0)
            try:
                fee_amount_str = str(fee_amount).strip() if fee_amount else '0'
                fee_amount = Decimal(fee_amount_str) if fee_amount_str else Decimal('0.00')
                if fee_amount < 0:
                    return JsonResponse({'error': 'Fee amount cannot be negative'}, status=400)
            except (ValueError, TypeError, InvalidOperation):
                return JsonResponse({'error': 'Invalid fee amount'}, status=400)
            
            fee = ShipmentFee(
                shipment=shipment,
                name=request.POST.get('fee_name'),
                amount=fee_amount,
                description=request.POST.get('fee_description', '')
            )
            
            try:
                fee.full_clean()
                fee.save()
            except ValidationError as e:
                return JsonResponse({'error': f'Invalid fee: {str(e)}'}, status=400)
            
            return redirect('admin_console')
        
        elif action == 'delete_shipment':
            shipment_id = request.POST.get('shipment_id')
            shipment = get_object_or_404(Shipment, id=shipment_id)
            shipment.delete()
            
            return redirect('admin_console')
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def chat_interface(request):
    """AI Chat interface endpoint"""
    return render(request, 'logistics/chat.html')
