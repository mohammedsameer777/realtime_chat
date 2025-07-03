from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from chat.models import ChatRequest, ChatMessage
import re

def sanitize_room_name(name):
    return re.sub(r"[^a-zA-Z0-9_.-]", "_", name)[:99]

@login_required
def room(request, room_name):
    name = request.GET.get("name", request.user.username)
    messages = ChatMessage.objects.filter(room_name=room_name).order_by("timestamp")
    return render(request, "chat/room.html", {
        "room_name": room_name,
        "username": request.user.username,
        "messages": messages
    })

@login_required
def request_test_page(request):
    return render(request, "chat/requests.html")

@login_required
@csrf_exempt
def send_chat_request(request):
    if request.method == "POST":
        sender = request.user
        receiver_username = request.POST.get("receiver")

        try:
            receiver = User.objects.get(username=receiver_username)
        except User.DoesNotExist:
            return JsonResponse({"error": "Receiver not found"}, status=404)

        if ChatRequest.objects.filter(sender=sender, receiver=receiver, status='pending').exists():
            return JsonResponse({"error": "Request already sent"}, status=400)

        ChatRequest.objects.create(sender=sender, receiver=receiver)
        return JsonResponse({"success": "Chat request sent"})

@require_GET
@login_required
def incoming_requests(request):
    user = request.user
    requests = ChatRequest.objects.filter(receiver=user, status__in=['pending', 'accepted'])
    data = [{"id": r.id, "from": r.sender.username, "status": r.status} for r in requests]
    return JsonResponse({"requests": data})

@login_required
@csrf_exempt
def respond_to_request(request):
    if request.method == "POST":
        request_id = request.POST.get("request_id")
        action = request.POST.get("action")

        try:
            chat_request = ChatRequest.objects.get(id=request_id, receiver=request.user)
        except ChatRequest.DoesNotExist:
            return JsonResponse({"error": "Chat request not found"}, status=404)

        if action == "accept":
            chat_request.status = "accepted"
            chat_request.save()
            room_name = sanitize_room_name(f"{chat_request.sender.username}_{chat_request.receiver.username}")

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{chat_request.sender.username}",
                {
                    "type": "chat.redirect",
                    "room": room_name
                }
            )

            return JsonResponse({
                "success": "Request accepted",
                "room": room_name
            })

        elif action == "reject":
            chat_request.status = "rejected"
            chat_request.save()
            return JsonResponse({"success": "Rejected"})

        else:
            return JsonResponse({"error": "Invalid action"}, status=400)
