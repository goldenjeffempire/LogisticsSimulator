from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils import timezone
from .models import Shipment, ShipmentFee, ShipmentHistory, PaymentTransaction
import json
from datetime import timedelta

def landing_page(request):
    """Dynamic landing page with hero, map, and live ticker"""
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
    return render(request, 'logistics/landing.html', context)


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


@csrf_exempt
def process_payment(request, tracking_id):
    """Process simulated payment transaction"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    shipment = get_object_or_404(Shipment, tracking_id=tracking_id)
    
    try:
        data = json.loads(request.body)
        cardholder_name = data.get('cardholder_name')
        card_number = data.get('card_number', '')
        
        if len(card_number) < 4:
            return JsonResponse({'error': 'Invalid card number'}, status=400)
        
        transaction = PaymentTransaction.objects.create(
            shipment=shipment,
            transaction_id=PaymentTransaction.generate_transaction_id(),
            amount=shipment.fee_amount,
            cardholder_name=cardholder_name,
            card_last_four=card_number[-4:],
            status='completed',
            completed_at=timezone.now()
        )
        
        shipment.fee_required = False
        shipment.status = 'in_transit'
        shipment.save()
        
        ShipmentHistory.objects.create(
            shipment=shipment,
            status='payment_completed',
            description=f'Payment of ${shipment.fee_amount} processed successfully'
        )
        
        return JsonResponse({
            'success': True,
            'transaction_id': transaction.transaction_id,
            'redirect_url': f'/tracking/{tracking_id}/confirmation/'
        })
        
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


@csrf_exempt
def admin_console(request):
    """Hidden admin console for shipment management"""
    if request.method == 'GET':
        shipments = Shipment.objects.all().order_by('-created_at')
        return render(request, 'logistics/admin_console.html', {'shipments': shipments})
    
    elif request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_shipment':
            tracking_id = Shipment.generate_tracking_id()
            shipment = Shipment.objects.create(
                tracking_id=tracking_id,
                owner_name=request.POST.get('owner_name'),
                owner_email=request.POST.get('owner_email'),
                owner_phone=request.POST.get('owner_phone'),
                owner_address=request.POST.get('owner_address'),
                status='label_created',
                current_location=request.POST.get('current_location', 'Processing Center'),
                destination=request.POST.get('destination'),
                fee_required=request.POST.get('fee_required') == 'on',
                fee_amount=request.POST.get('fee_amount', 0),
            )
            
            ShipmentHistory.objects.create(
                shipment=shipment,
                status='label_created',
                location=shipment.current_location,
                description='Shipment label created'
            )
            
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
                    description=f'Status updated to {new_status}'
                )
            
            shipment.current_location = new_location
            shipment.fee_required = request.POST.get('fee_required') == 'on'
            shipment.fee_amount = request.POST.get('fee_amount', shipment.fee_amount)
            shipment.save()
            
            return redirect('admin_console')
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def chat_interface(request):
    """AI Chat interface endpoint"""
    return render(request, 'logistics/chat.html')
