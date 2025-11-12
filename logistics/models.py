from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
import random
import string

class Shipment(models.Model):
    """Model for tracking shipments in the logistics system"""
    
    STATUS_CHOICES = [
        ('label_created', 'Label Created'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('arrived_facility', 'Arrived at Facility'),
        ('out_for_delivery', 'Out for Delivery'),
        ('processing_hold', 'Processing Hold'),
        ('delivered', 'Delivered'),
    ]
    
    tracking_id = models.CharField(max_length=50, unique=True, db_index=True)
    owner_name = models.CharField(max_length=200)
    owner_email = models.EmailField(blank=True, null=True)
    owner_phone = models.CharField(max_length=20, blank=True, null=True)
    owner_address = models.TextField(blank=True, null=True)
    
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='label_created')
    current_location = models.CharField(max_length=200, blank=True, null=True)
    destination = models.CharField(max_length=200, blank=True, null=True)
    
    fee_required = models.BooleanField(default=False)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))])
    
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    dimensions = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estimated_delivery = models.DateTimeField(blank=True, null=True)
    
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tracking_id']),
            models.Index(fields=['owner_name']),
        ]
    
    def __str__(self):
        return f"{self.tracking_id} - {self.owner_name}"
    
    @classmethod
    def generate_tracking_id(cls):
        """Generate a unique tracking ID"""
        while True:
            number = ''.join(random.choices(string.digits, k=6))
            tracking_id = f"US-9000-TKG-{number}"
            if not cls.objects.filter(tracking_id=tracking_id).exists():
                return tracking_id


class ShipmentFee(models.Model):
    """Model for individual fees associated with a shipment"""
    
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='fees')
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        """Validate fee data"""
        if self.amount < 0:
            raise ValidationError({'amount': 'Fee amount cannot be negative'})
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.name} - ${self.amount}"


class ShipmentHistory(models.Model):
    """Model for tracking shipment status history"""
    
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='history')
    status = models.CharField(max_length=50)
    location = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['timestamp']
        verbose_name_plural = 'Shipment histories'
    
    def __str__(self):
        return f"{self.shipment.tracking_id} - {self.status} - {self.timestamp}"


class PaymentTransaction(models.Model):
    """Model for tracking simulated payment transactions"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='payments')
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    cardholder_name = models.CharField(max_length=200)
    card_last_four = models.CharField(max_length=4)
    card_type = models.CharField(max_length=20, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.transaction_id} - ${self.amount}"
    
    @classmethod
    def generate_transaction_id(cls):
        """Generate a unique transaction ID"""
        while True:
            transaction_id = 'TXN-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
            if not cls.objects.filter(transaction_id=transaction_id).exists():
                return transaction_id
