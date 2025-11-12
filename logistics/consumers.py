import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Shipment
import asyncio
import random

class TrackingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.tracking_id = self.scope['url_route']['kwargs']['tracking_id']
        self.room_group_name = f'tracking_{self.tracking_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        
        shipment = await self.get_shipment(self.tracking_id)
        if shipment:
            await self.send(text_data=json.dumps({
                'type': 'status_update',
                'status': shipment.status,
                'location': shipment.current_location,
                'message': f'Connected to tracking {self.tracking_id}'
            }))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'request_update':
            shipment = await self.get_shipment(self.tracking_id)
            if shipment:
                await self.send(text_data=json.dumps({
                    'type': 'status_update',
                    'status': shipment.status,
                    'location': shipment.current_location,
                    'fee_required': shipment.fee_required,
                    'fee_amount': str(shipment.fee_amount)
                }))

    async def status_update(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_shipment(self, tracking_id):
        try:
            return Shipment.objects.get(tracking_id=tracking_id)
        except Shipment.DoesNotExist:
            return None


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        
        await self.send(text_data=json.dumps({
            'type': 'system',
            'message': 'Welcome to Global Logistics Support! How can I assist you today?'
        }))

    async def disconnect(self, code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
        data = json.loads(text_data)
        message = data.get('message', '').lower()
        
        await asyncio.sleep(random.uniform(0.8, 1.8))
        
        response = await self.generate_response(message)
        
        await self.send(text_data=json.dumps({
            'type': 'bot',
            'message': response
        }))

    async def generate_response(self, message):
        responses = {
            'hello': 'Hello! Welcome to Global Logistics Network. How can I assist you today?',
            'hi': 'Hi there! I\'m your AI support assistant. How may I help you?',
            'help': 'I can help you track shipments, understand fees, and answer questions about our logistics services.',
            'track': 'To track your shipment, please provide your tracking number in the format US-9000-TKG-XXXXXX.',
            'fee': 'Fees may include import duty, brokerage fees, storage fees, and documentation fees. Would you like more details about a specific fee?',
            'payment': 'You can process payments securely through our payment gateway. We accept all major credit cards.',
            'delivery': 'Standard delivery takes 3-5 business days. Express options are available for faster delivery.',
            'status': 'To check your shipment status, please provide your tracking number.',
            'thank': 'You\'re welcome! Is there anything else I can help you with?',
            'bye': 'Thank you for contacting Global Logistics Network. Have a great day!',
        }
        
        for keyword, response in responses.items():
            if keyword in message:
                return response
        
        return 'I understand you have a question. For specific assistance, please provide your tracking number or contact our support team directly.'
