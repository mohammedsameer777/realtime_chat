from django.db import models
from django.utils import timezone
from django.conf import settings


class Chat(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_chats'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_chats'
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Chat between {self.sender.username} and {self.receiver.username}"


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp}"
