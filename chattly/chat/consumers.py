import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "test-room"

        print(f"@CONNECT {self.channel_name=}")

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        print("Disconnected")

    async def receive(self, text_data):
        receive_dict = json.loads(text_data)
        action = receive_dict["action"]
        print(f"@RECEIVE - receive_dict: {receive_dict['action']}")

        if (action == "new-offer") or (action == "new-answer"):
            receiver_channel_name = receive_dict["message"]["receiver_channel_name"]

            if receiver_channel_name != self.channel_name:
                receive_dict["message"]["receiver_channel_name"] = self.channel_name

                await self.channel_layer.send(
                    receiver_channel_name,
                    {"type": "send.sdp", "receive_dict": receive_dict},
                )

        else:
            receive_dict["message"]["receiver_channel_name"] = self.channel_name
            print(receive_dict["message"])

            await self.channel_layer.group_send(
                self.room_group_name, {"type": "send.sdp", "receive_dict": receive_dict}
            )

    async def send_sdp(self, event):
        print(f"send sdp {event=}")
        receive_dict = event["receive_dict"]

        await self.send(text_data=json.dumps(receive_dict))