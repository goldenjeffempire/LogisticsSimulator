import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import asyncio
import random

class StatusTickerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.should_send = True
        asyncio.create_task(self.send_status_updates())
    
    async def disconnect(self, close_code):
        self.should_send = False
    
    async def send_status_updates(self):
        statuses = [
            "✓ New York Hub: 47 shipments processed",
            "✓ Chicago Distribution: 32 packages sorted",
            "✓ Los Angeles Terminal: 28 deliveries en route",
            "✓ Miami Gateway: 19 international arrivals",
            "✓ Dallas Hub: 41 packages in transit",
            "✓ Seattle Terminal: 23 shipments cleared customs"
        ]
        
        while self.should_send:
            status = random.choice(statuses)
            await self.send(text_data=json.dumps({
                'type': 'status_update',
                'message': status
            }))
            await asyncio.sleep(3)
