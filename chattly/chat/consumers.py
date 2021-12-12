import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from datetime import datetime
from urllib.parse import parse_qs


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.query_params = parse_qs(self.scope["query_string"].decode())
        self.username = self.query_params["username"][-1]

        self.chatroom_name = self.scope["url_route"]["kwargs"]["chatroomName"].lower()
        self.room_group_name = f"chat_{self.chatroom_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        receive_data = json.loads(
            text_data
        )  # this will be sent over websocket in 'send_sdp' and 'chat_message'

        msg_type = receive_data["msgType"]

        # NEW-OFFER / NEW-ANSWER
        if msg_type in ("new_offer", "new_answer"):
            receiver_channel_name = receive_data["message"]["receiver_channel_name"]

            # dont send to sender
            if receiver_channel_name != self.channel_name:
                receive_data["message"]["receiver_channel_name"] = self.channel_name

                await self.channel_layer.send(
                    receiver_channel_name,
                    {"type": "send.sdp", "receive_data": receive_data},
                )

        # NEW-PEER
        elif msg_type == "new_peer":
            receive_data["message"]["receiver_channel_name"] = self.channel_name

            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "send_sdp", "receive_data": receive_data},
            )

        # CHAT_MESSAGE
        elif msg_type == "chat_message":
            dt = timezone.now()
            receive_data["message"]["dt"] = datetime.timestamp(dt)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "receive_data": receive_data,
                },
            )
        # FIXME
        else:
            print(f"UNKNOWN msg_type {msg_type=}")

    # WebRTC protocol
    async def send_sdp(self, event):
        receive_data = event["receive_data"]

        await self.send(text_data=json.dumps(receive_data))

    async def chat_message(self, event):
        # send message to websocket
        receive_data = event["receive_data"]

        await self.send(text_data=json.dumps(receive_data))
