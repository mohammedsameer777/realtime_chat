from django.urls import path
from . import views

urlpatterns = [
    path("test-requests/", views.request_test_page, name="test_requests"),
    path("send-request/", views.send_chat_request),
    path("incoming-requests/", views.incoming_requests),
    path("respond-request/", views.respond_to_request),
    path("<str:room_name>/", views.room, name="room"),
]
