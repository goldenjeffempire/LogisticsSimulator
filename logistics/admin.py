from django.contrib import admin
from .models import Shipment, ShipmentFee, ShipmentHistory, PaymentTransaction

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('tracking_id', 'owner_name', 'status', 'current_location', 'fee_required', 'created_at')
    list_filter = ('status', 'fee_required', 'created_at')
    search_fields = ('tracking_id', 'owner_name', 'owner_email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Tracking Information', {
            'fields': ('tracking_id', 'status', 'current_location', 'destination')
        }),
        ('Owner Information', {
            'fields': ('owner_name', 'owner_email', 'owner_phone', 'owner_address')
        }),
        ('Fee Information', {
            'fields': ('fee_required', 'fee_amount')
        }),
        ('Package Details', {
            'fields': ('weight', 'dimensions', 'estimated_delivery', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(ShipmentFee)
class ShipmentFeeAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'name', 'amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('shipment__tracking_id', 'name')

@admin.register(ShipmentHistory)
class ShipmentHistoryAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'status', 'location', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('shipment__tracking_id', 'location', 'description')
    readonly_fields = ('timestamp',)

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'shipment', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('transaction_id', 'shipment__tracking_id', 'cardholder_name')
    readonly_fields = ('created_at', 'completed_at')
