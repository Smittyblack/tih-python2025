import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging

logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info(f"Connecting user: {self.scope['user']}")
        if self.scope['user'].is_authenticated:
            self.group_name = f'notifications_{self.scope["user"].id}'
            logger.info(f"Adding to group: {self.group_name}")
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            logger.info("User not authenticated, closing connection")
            await self.close()

    async def disconnect(self, close_code):
        logger.info(f"Disconnecting with code: {close_code}")
        if self.scope['user'].is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notification(self, event):
        logger.info(f"Sending notification: {event}")
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'link': event.get('post_link', ''),
            'created_at': event['created_at'],
            'post_title': event.get('post_title', '')
        }))