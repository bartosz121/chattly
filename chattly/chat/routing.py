from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path(r"ws/chatroom/<slug:chatroomName>", consumers.ChatConsumer.as_asgi()),
]
