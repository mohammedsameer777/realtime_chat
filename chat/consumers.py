import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

class ChatRequestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f"user_{self.user_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        from .models import Chat  # ✅ Import inside method
        data = json.loads(text_data)
        msg_type = data.get('type')

        if msg_type == 'request':
            await self.channel_layer.group_send(
                f"user_{data['receiver_id']}",
                {
                    'type': 'receive_request',
                    'from_user': data['sender_id'],
                    'from_username': data['sender_username']
                }
            )

        elif msg_type == 'accept':
            sender_id = int(data['sender_id'])
            receiver_id = int(data['receiver_id'])
            chat = await self.create_or_get_chat(sender_id, receiver_id)

            for uid in [sender_id, receiver_id]:
                await self.channel_layer.group_send(
                    f"user_{uid}",
                    {
                        "type": "redirect",
                        "chat_id": chat.id
                    }
                )

    async def receive_request(self, event):
        await self.send(text_data=json.dumps({
            'type': 'request',
            'from_user': event['from_user'],
            'from_username': event['from_username']
        }))

    async def redirect(self, event):
        await self.send(text_data=json.dumps({
            'type': 'redirect',
            'chat_id': event['chat_id']
        }))

    @database_sync_to_async
    def create_or_get_chat(self, sender_id, receiver_id):
        from .models import Chat  # ✅ Safe import
        chat, _ = Chat.objects.get_or_create(sender_id=sender_id, receiver_id=receiver_id)
        return chat


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.group_name = f"chat_{self.chat_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender_username = data['sender']
        await self.save_message(sender_username, self.chat_id, message)

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'sender': sender_username,
                'message': message,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'sender': event['sender'],
            'message': event['message']
        }))

    @database_sync_to_async
    def save_message(self, sender_username, chat_id, content):
        from .models import Chat, Message  # ✅ Import here
        User = get_user_model()
        sender = User.objects.get(username=sender_username)
        chat = Chat.objects.get(id=chat_id)
        Message.objects.create(chat=chat, sender=sender, content=content)
