from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .models import Chat, Message

User = get_user_model()

@login_required
def home(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'chat/home.html', {'users': users})

@login_required
def chatroom(request, chat_id):
    return render(request, 'chat/chatroom.html', {
        'chat_id': chat_id,
    })

@login_required
def get_messages(request, chat_id):
    try:
        chat = Chat.objects.get(id=chat_id)  # FIX: from `chat_id=chat_id` to `id=chat_id`
    except Chat.DoesNotExist:
        return JsonResponse([], safe=False)

    msgs = chat.messages.all().order_by('timestamp')
    data = [
        {
            'sender': m.sender.username,
            'content': m.content,
            'timestamp': m.timestamp.strftime('%H:%M'),
        }
        for m in msgs
    ]
    return JsonResponse(data, safe=False)
