"""
Finance Service Layer
Handles all financial operations including fee calculations and payment processing.
"""
from decimal import Decimal
from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from ..models import Shipment, ShipmentFee, PaymentTransaction


class FinanceService:
    """Service for handling financial operations"""
    
    @staticmethod
    @transaction.atomic
    def recalculate_shipment_fees(shipment):
        """
        Recalculate total fee amount for a shipment based on individual fees.
        This ensures data consistency between ShipmentFee items and Shipment.fee_amount.
        
        Args:
            shipment: Shipment instance to recalculate fees for
            
        Returns:
            Decimal: The new total fee amount
        """
        total = Decimal('0.00')
        fees = shipment.fees.all()
        
        for fee in fees:
            total += fee.amount
        
        shipment.fee_amount = total
        shipment.fee_required = total > 0
        shipment.save(update_fields=['fee_amount', 'fee_required'])
        
        return total
    
    @staticmethod
    @transaction.atomic
    def process_payment(shipment, cardholder_name, card_number, expiry_date=None, cvv=None):
        """
        Process a payment transaction with idempotency and atomicity.
        Prevents double-charge by checking for recent completed transactions.
        
        Args:
            shipment: Shipment to process payment for
            cardholder_name: Name on the card
            card_number: Card number (will extract last 4 digits)
            expiry_date: Card expiry date (optional for simulation)
            cvv: Card CVV (optional for simulation)
            
        Returns:
            tuple: (success: bool, transaction: PaymentTransaction or None, error: str or None)
        """
        if not shipment.fee_required:
            return False, None, "No payment required for this shipment"
        
        recent_payment = shipment.payments.filter(
            status='completed',
            created_at__gte=timezone.now() - timedelta(minutes=5)
        ).first()
        
        if recent_payment:
            return False, None, f"Payment already processed: {recent_payment.transaction_id}"
        
        if not cardholder_name or not card_number:
            return False, None, "Missing required payment information"
        
        if len(card_number.replace(' ', '')) < 4:
            return False, None, "Invalid card number"
        
        fees = shipment.fees.all()
        total_fee = sum(fee.amount for fee in fees) or shipment.fee_amount
        
        if total_fee <= 0:
            return False, None, "Invalid fee amount"
        
        try:
            transaction = PaymentTransaction.objects.create(
                shipment=shipment,
                transaction_id=PaymentTransaction.generate_transaction_id(),
                amount=total_fee,
                cardholder_name=cardholder_name,
                card_last_four=card_number.replace(' ', '')[-4:],
                status='completed',
                completed_at=timezone.now()
            )
            
            shipment.fee_required = False
            shipment.status = 'in_transit'
            shipment.save(update_fields=['fee_required', 'status'])
            
            from ..models import ShipmentHistory
            ShipmentHistory.objects.create(
                shipment=shipment,
                status='payment_completed',
                description=f'Payment of ${total_fee} processed successfully (Transaction: {transaction.transaction_id})'
            )
            
            return True, transaction, None
            
        except Exception as e:
            return False, None, str(e)
    
    @staticmethod
    def calculate_fee_breakdown(shipment):
        """
        Get a detailed breakdown of all fees for a shipment.
        
        Args:
            shipment: Shipment instance
            
        Returns:
            dict: Fee breakdown with individual fees and total
        """
        fees = list(shipment.fees.all())
        total = sum(fee.amount for fee in fees)
        
        return {
            'fees': fees,
            'total': total,
            'count': len(fees),
            'shipment_total': shipment.fee_amount,
            'synchronized': total == shipment.fee_amount
        }
