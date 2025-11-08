from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from logistics.models import Shipment, ShipmentFee, ShipmentHistory

class Command(BaseCommand):
    help = 'Seed database with demo shipment data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding demo shipments...')
        
        shipment1 = Shipment.objects.create(
            tracking_id='US-9000-TKG-938711',
            owner_name='John A. Doe',
            owner_email='john.doe@example.com',
            owner_phone='(555) 123-4567',
            owner_address='1247 Commerce Street, Dallas, TX 75201',
            status='processing_hold',
            current_location='Dallas Distribution Center',
            destination='Dallas, TX',
            fee_required=True,
            fee_amount=271.00,
            weight=12.5,
            dimensions='18x12x10 inches',
            estimated_delivery=timezone.now() + timedelta(days=2)
        )
        
        ShipmentFee.objects.create(
            shipment=shipment1,
            name='Import Duty',
            amount=125.00,
            description='US Customs import duty'
        )
        ShipmentFee.objects.create(
            shipment=shipment1,
            name='Brokerage Fee',
            amount=75.50,
            description='Customs clearance brokerage'
        )
        ShipmentFee.objects.create(
            shipment=shipment1,
            name='Storage Fee',
            amount=42.00,
            description='Warehouse storage charges'
        )
        ShipmentFee.objects.create(
            shipment=shipment1,
            name='Documentation Fee',
            amount=28.50,
            description='Processing and documentation'
        )
        
        ShipmentHistory.objects.create(
            shipment=shipment1,
            status='label_created',
            location='Los Angeles, CA',
            description='Shipping label created',
            timestamp=timezone.now() - timedelta(days=5)
        )
        ShipmentHistory.objects.create(
            shipment=shipment1,
            status='picked_up',
            location='Los Angeles, CA',
            description='Package picked up from sender',
            timestamp=timezone.now() - timedelta(days=4, hours=18)
        )
        ShipmentHistory.objects.create(
            shipment=shipment1,
            status='in_transit',
            location='Phoenix, AZ',
            description='In transit to destination',
            timestamp=timezone.now() - timedelta(days=3, hours=12)
        )
        ShipmentHistory.objects.create(
            shipment=shipment1,
            status='arrived_facility',
            location='Dallas Distribution Center',
            description='Arrived at sorting facility',
            timestamp=timezone.now() - timedelta(days=2, hours=8)
        )
        ShipmentHistory.objects.create(
            shipment=shipment1,
            status='processing_hold',
            location='Dallas Distribution Center',
            description='HOLD: Outstanding fees required for release',
            timestamp=timezone.now() - timedelta(days=1, hours=2)
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created shipment: {shipment1.tracking_id}'))
        
        shipment2 = Shipment.objects.create(
            tracking_id='US-9000-TKG-847291',
            owner_name='Sarah Mitchell',
            owner_email='sarah.mitchell@example.com',
            owner_phone='(555) 234-5678',
            owner_address='892 Market Street, San Francisco, CA 94102',
            status='out_for_delivery',
            current_location='San Francisco Distribution Center',
            destination='San Francisco, CA',
            fee_required=False,
            fee_amount=0.00,
            weight=5.2,
            dimensions='12x8x6 inches',
            estimated_delivery=timezone.now() + timedelta(hours=4)
        )
        
        ShipmentHistory.objects.create(
            shipment=shipment2,
            status='label_created',
            location='New York, NY',
            description='Shipping label created',
            timestamp=timezone.now() - timedelta(days=3)
        )
        ShipmentHistory.objects.create(
            shipment=shipment2,
            status='picked_up',
            location='New York, NY',
            description='Package picked up',
            timestamp=timezone.now() - timedelta(days=2, hours=20)
        )
        ShipmentHistory.objects.create(
            shipment=shipment2,
            status='in_transit',
            location='Chicago, IL',
            description='In transit via air freight',
            timestamp=timezone.now() - timedelta(days=1, hours=14)
        )
        ShipmentHistory.objects.create(
            shipment=shipment2,
            status='arrived_facility',
            location='San Francisco Distribution Center',
            description='Arrived at local facility',
            timestamp=timezone.now() - timedelta(hours=8)
        )
        ShipmentHistory.objects.create(
            shipment=shipment2,
            status='out_for_delivery',
            location='San Francisco Distribution Center',
            description='Out for delivery - Delivery expected today',
            timestamp=timezone.now() - timedelta(hours=2)
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created shipment: {shipment2.tracking_id}'))
        
        shipment3 = Shipment.objects.create(
            tracking_id='US-9000-TKG-562483',
            owner_name='Michael Chen',
            owner_email='michael.chen@example.com',
            owner_phone='(555) 345-6789',
            owner_address='1523 Broadway, New York, NY 10036',
            status='delivered',
            current_location='Delivered',
            destination='New York, NY',
            fee_required=False,
            fee_amount=0.00,
            weight=8.7,
            dimensions='14x10x8 inches',
            estimated_delivery=timezone.now() - timedelta(days=1)
        )
        
        ShipmentHistory.objects.create(
            shipment=shipment3,
            status='label_created',
            location='Seattle, WA',
            description='Shipping label created',
            timestamp=timezone.now() - timedelta(days=4)
        )
        ShipmentHistory.objects.create(
            shipment=shipment3,
            status='picked_up',
            location='Seattle, WA',
            description='Package picked up',
            timestamp=timezone.now() - timedelta(days=3, hours=18)
        )
        ShipmentHistory.objects.create(
            shipment=shipment3,
            status='in_transit',
            location='Denver, CO',
            description='In transit - Ground shipping',
            timestamp=timezone.now() - timedelta(days=2, hours=10)
        )
        ShipmentHistory.objects.create(
            shipment=shipment3,
            status='arrived_facility',
            location='New York Distribution Center',
            description='Arrived at destination facility',
            timestamp=timezone.now() - timedelta(days=1, hours=12)
        )
        ShipmentHistory.objects.create(
            shipment=shipment3,
            status='out_for_delivery',
            location='New York Distribution Center',
            description='Out for delivery',
            timestamp=timezone.now() - timedelta(days=1, hours=6)
        )
        ShipmentHistory.objects.create(
            shipment=shipment3,
            status='delivered',
            location='New York, NY',
            description='Successfully delivered - Signature obtained',
            timestamp=timezone.now() - timedelta(days=1, hours=2)
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created shipment: {shipment3.tracking_id}'))
        
        self.stdout.write(self.style.SUCCESS('\nDemo data seeded successfully!'))
        self.stdout.write(self.style.WARNING(f'\nShipment with fees: {shipment1.tracking_id}'))
        self.stdout.write(self.style.WARNING(f'Total demo shipments: 3'))
