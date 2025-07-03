# test_save_message.py

import os
import django

# ✅ SET YOUR PROJECT NAME HERE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')  # change if not 'django_project'
django.setup()

from chat.models import ChatMessage
from django.contrib.auth.models import User

# ✅ Change these values based on your users and room
room_name = "user0001_user0002"
username = "user0001"

try:
    user = User.objects.get(username=username)
    ChatMessage.objects.create(
        room_name=room_name,
        sender=user,
        message="Hello from test script!"
    )
    print(f"✅ Message saved to room '{room_name}' from user '{username}'")
except User.DoesNotExist:
    print(f"❌ User '{username}' does not exist. Please create it first with: python manage.py createsuperuser")
