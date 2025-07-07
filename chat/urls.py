from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('chatroom/<str:chat_id>/', views.chatroom, name='chatroom'),
    path('messages/<str:chat_id>/', views.get_messages, name='get_messages'),
]
