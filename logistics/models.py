from django.db import models
import random
import string

def generate_tracking_number():
    random_part = ''.join(random.choices(string.digits, k=6))
    return f"US-9000-TKG-{random_part}"

class Shipment(models.Model):
    tracking_number = models.CharField(max_length=50, unique=True, default=generate_tracking_number)
    owner_name = models.CharField(max_length=200)
    fee_required = models.BooleanField(default=True)
    fees = models.JSONField(default=list)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=80.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    status = models.CharField(max_length=50, default='In Transit')
    origin = models.CharField(max_length=200, default='New York, NY')
    destination = models.CharField(max_length=200, default='Los Angeles, CA')
    
    def __str__(self):
        return f"{self.tracking_number} - {self.owner_name}"
    
    def save(self, *args, **kwargs):
        if not self.fees:
            self.fees = [
                {"name": "Customs Duty", "amount": 35.00},
                {"name": "Brokerage Fee", "amount": 25.00},
                {"name": "Processing Fee", "amount": 20.00}
            ]
        if self.fees:
            self.total_amount = sum(float(fee.get('amount', 0)) for fee in self.fees)
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']
