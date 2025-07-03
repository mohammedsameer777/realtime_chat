import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from .models import ChatMessage


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        # Personal user group (for notifications like redirect or new requests)
        self.user_group = None
        if self.scope["user"].is_authenticated:
            self.user_group = f"user_{self.scope['user'].username}"
            await self.channel_layer.group_add(self.user_group, self.channel_name)

        # Join chat room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        if self.user_group:
            await self.channel_layer.group_discard(self.user_group, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender_username = data['sender']

        # ✅ Save to DB
        await self.save_message(self.room_name, sender_username, message)

        # ✅ Broadcast to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender_username
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'sender': event['sender'],
            'message': event['message']
        }))

    async def chat_redirect(self, event):
        await self.send(text_data=json.dumps({
            "type": "redirect",
            "room": event["room"]
        }))

    async def request_new(self, event):
        await self.send(text_data=json.dumps({
            "type": "request",
            "from": event["from_user"],
            "request_id": event["request_id"]
        }))

    @sync_to_async
    def save_message(self, room_name, sender_username, message):
        user = User.objects.get(username=sender_username)
        ChatMessage.objects.create(
            room_name=room_name,
            sender=user,
            message=message
        )
