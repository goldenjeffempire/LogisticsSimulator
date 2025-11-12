"""
Django signals for automatic data synchronization
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ShipmentFee
from .services.finance import FinanceService


@receiver(post_save, sender=ShipmentFee)
def recalculate_fees_on_save(sender, instance, created, **kwargs):
    """
    Automatically recalculate shipment total fees when a fee is created or updated.
    This ensures the Shipment.fee_amount always stays in sync with individual fees.
    """
    FinanceService.recalculate_shipment_fees(instance.shipment)


@receiver(post_delete, sender=ShipmentFee)
def recalculate_fees_on_delete(sender, instance, **kwargs):
    """
    Automatically recalculate shipment total fees when a fee is deleted.
    """
    FinanceService.recalculate_shipment_fees(instance.shipment)
