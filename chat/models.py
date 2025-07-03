from django.db import models
from django.contrib.auth.models import User

class ChatRequest(models.Model):
    sender = models.ForeignKey(User, related_name='sent_chat_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_chat_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ], default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} ➝ {self.receiver} ({self.status})"
class ChatMessage(models.Model):
    room_name = models.CharField(max_length=255)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.room_name}] {self.sender.username}: {self.message[:20]}"