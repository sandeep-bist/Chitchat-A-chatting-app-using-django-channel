import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from chat.models import Chat, UserProfileModel,ChatGroup,GroupMessage
# from accounts.models import User
from django.contrib.auth import get_user_model
User=get_user_model()

class PersonalChatConsumer(AsyncWebsocketConsumer):
    online_user=set()
    async def connect(self):
        self.user=self.scope['user']
        print(self.user,"Testing connection and redis PersonalChatConsumer",self.channel_name)
        if self.user.is_authenticated:
            self.user_id=self.user.id
            chat_with_user=self.scope['url_route']['kwargs']['id']
            user_ids=[int(self.user.id),int(chat_with_user)]
            user_ids=sorted(user_ids)
            self.room_groups_name=f"chat_{user_ids[0]}-{user_ids[1]}"
            await self.add_user_to_online_list(self.user)
            await self.channel_layer.group_add(
                "online_users",
                self.channel_name
            )
            await self.update_user_status(self.user, 'online')
            await self.channel_layer.group_add(
                self.room_groups_name,
                self.channel_name
            )
            await self.accept()  


    async def receive(self, text_data=None, bytes_data=None):
        # sourcery skip: avoid-builtin-shadow
        data = json.loads(text_data)
        print(data,"recieved dataa",self.room_groups_name)
        message_type = data.get('type', None)
        id = data.get('id', None)
        reciever_id = data.get('reciever_id', None)
        # await self.channel_layer.group_send(
        #     self.room_groups_name,
        #     {
        #         "type": "chat_message",
        #         "message": message,
        #         "id": id,
        #         "reciever_id":reciever_id
        #     }
        # )
        if message_type == 'chat_message':
            message = data['message']
            await self.send_chat_message( id,message,reciever_id)
            await self.save_message_to_db(id, self.room_groups_name, message,reciever_id) 
        elif message_type == 'typing':
            await self.broadcast_typing_status(id, True)
        elif message_type == 'stop_typing':
            await self.broadcast_typing_status(id, False)

        
    
    
    
    async def send_chat_message(self, id,message,reciever_id):
        await self.channel_layer.group_send(
            self.room_groups_name,
            {
                "type": "chat_message",
                "message": message,
                "id": id,
                "reciever_id":reciever_id
            }
        )

    async def broadcast_typing_status(self, username, is_typing):
        await self.channel_layer.group_send(
            self.room_groups_name,
            {
                'type': 'typing_status',
                'username': username,
                'is_typing': is_typing
            }
        )

    async def typing_status(self, event):
        username = event['username']
        is_typing = event['is_typing']

        await self.send(text_data=json.dumps({
            'type': 'typing_status',
            'username': username,
            'is_typing': is_typing
        }))
    
    # async def chat_message(self, event):
    #     message = event['message']
    #     username = event['username']

    #     await self.send(text_data=json.dumps({
    #         'type': 'chat_message',
    #         'message': message,
    #         'username': username
    #     }))

    
    
    
    async def disconnect(self, code):
        print("Testing disconnect PersonalChatConsumer",self.room_groups_name)
        if self.user.is_authenticated:
            await self.update_user_status(self.user, 'offline')
            await self.channel_layer.group_discard(
                "online_users",
                self.channel_name
            )
            await self.remove_user_from_online_list(self.user)
        self.channel_layer.group_discard(
            self.room_groups_name,
            self.channel_name
        )
        
    async def chat_message(self, event):
        message = event['message']
        id = event['id']
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "message":message,
            "id":id
        }))
    
    async def update_user_status(self, user, status):
        # Broadcast the status update to all clients
        await self.channel_layer.group_send(
            "online_users",
            {
                'type': 'user_status',
                'username': user.email,
                'status': status
            }
        )

    async def user_status(self, event):
        username = event['username']
        status = event['status']
        print("User status",PersonalChatConsumer.online_user)
        # Send the status update to the WebSocket client
        await self.send(text_data=json.dumps({
            "type": "online_user",
            
            'username': list(PersonalChatConsumer.online_user),
            'status': status
        }))

    @database_sync_to_async
    def add_user_to_online_list(self, user):
        # Add the user to an online users list, for example, a Redis set
        PersonalChatConsumer.online_user.add(self.user.id)
        
        # pass

    @database_sync_to_async
    def remove_user_from_online_list(self, user):
        # Remove the user from the online users list
        print(self.user.id,"remove the user from the online users list",PersonalChatConsumer.online_user)
        if self.user.id in PersonalChatConsumer.online_user:
            PersonalChatConsumer.online_user.remove(self.user.id)
        
        # pass
        
    
    @database_sync_to_async
    def save_message_to_db(self, sender_id, thread_name, message,reciever_id):
        chat_obj = Chat.objects.create(sender_id=sender_id, thread_name=thread_name, message=message,reciever_id=reciever_id)
        
        
        
class OnlineStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'user'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        # await self.send(
        #     json.dumps({
        #         "type": "welcome_message",
        #         "message": "Hey there! You've successfully connected!",
        #     })
        # )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        print('data---recieved',data)
        username = data['username']
        connection_type = data['type']
        print(connection_type)
        await self.change_online_status(username, connection_type)

    async def send_onlineStatus(self, event):
        data = json.loads(event.get('value'))
        username = data['username']
        online_status = data['status']
        await self.send(text_data=json.dumps({
            'username':username,
            'online_status':online_status
        }))


    async def disconnect(self, message):
        self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @database_sync_to_async
    def change_online_status(self, username, c_type):
        user = User.objects.get(username=username)
        userprofile = UserProfileModel.objects.get(user=user)
        userprofile.online_status = c_type == 'open'
        userprofile.save()

class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = self.scope['url_route']['kwargs']['group_name']
        self.group_room_name = f'group_chat_{self.group_name}'

        # Join group chat room
        await self.channel_layer.group_add(
            self.group_room_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave group chat room
        await self.channel_layer.group_discard(
            self.group_room_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(data,"-------------------group chat recive data------------------------")
        
        message_type = data.get('type', None)
        group_id = data.get('reciever_id', None)
        
        sender_id = data.get('typing_user_id', None)
        if message_type == 'chat_message':
            sender_id = data.get('id', None)
            sender_name,sender_email=await self.get_userdetail_from_db(sender_id)
            message = data['message']
            await self.send_chat_message( message,sender_id,sender_email,sender_name)
            await self.save_message(sender_id, group_id, message)    
            
        elif message_type == 'typing':
            typing_user_id = data.get('typing_user_id', None)  
            sender_name,sender_email=await self.get_userdetail_from_db(typing_user_id)
            await self.broadcast_typing_status(typing_user_id,True,sender_name,sender_email)
        elif message_type == 'stop_typing':
            typing_user_id = data.get('typing_user_id', None)  
            sender_name,sender_email=await self.get_userdetail_from_db(typing_user_id)                  
            await self.broadcast_typing_status(typing_user_id, False,sender_name,sender_email)
        
            
    async def send_chat_message(self, message,sender_id,sender_email,sender_name):
        await self.channel_layer.group_send(
            self.group_room_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': sender_id,
                "sender_name":sender_name,
                "sender_email": sender_email
            }
        )

    async def broadcast_typing_status(self, username, is_typing,sender_name,sender_email):
        await self.channel_layer.group_send(
            self.group_room_name,
            {
                'type': 'typing_status',
                'username': username,
                'is_typing': is_typing,
                "is_group_message": True,
                "sender_name":sender_name,
                "sender_email":sender_email
                
            }
        )

    async def typing_status(self, event):
        username = event['username']
        is_typing = event['is_typing']
        sender_name = event['sender_name']
        sender_email = event['sender_email']

        await self.send(text_data=json.dumps({
            'type': 'typing_status',
            'username': username,
            'is_typing': is_typing,
            "is_group_message": True,
            "sender_email":sender_email
        }))



    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        sender_name = event['sender_name']
        sender_email = event['sender_email']
        # print(event,"------------------------>>>>>>> Message")
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            'message': message,
            'id': username,
            "sender_name": sender_name,
            "sender_email": sender_email,
        }))

    @sync_to_async
    def get_userdetail_from_db(self, sender_id):
        if sender_id is not None:
            sender_id = int(sender_id)
            sender = User.objects.get(id=sender_id)
            sender_name = f'{sender.first_name} {sender.last_name}'
            sender_email = sender.email
            return sender_name,sender_email
        

    @sync_to_async
    def save_message(self, sender_id, group_id, message):
        user = User.objects.get(id=sender_id)
        room = ChatGroup.objects.get(id=group_id)

        GroupMessage.objects.create(user=user, group=room, content=message)
        # sender_name = f'{user.first_name} {user.last_name}'
        # sender_email = user.email
        # return sender_name,sender_email
    
    
class oLDGroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("Testing connection and redis GroupChatConsumer",self.channel_name)
        
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))
        
        

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        my_id = self.scope['user'].id
        self.room_group_name = f'{my_id}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, code):
        self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        data = json.loads(event.get('value'))
        count = data['count']
        print(count)
        await self.send(text_data=json.dumps({
            'count':count
        }))
        
        
