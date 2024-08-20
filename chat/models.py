from django.db import models
from django.contrib.auth import get_user_model
User=get_user_model()
# Create your models here.


class Chat(models.Model):
    sender_id = models.IntegerField(blank=True, null=True)
    thread_name = models.CharField(blank=True, null=True, max_length=20)
    message = models.TextField(blank=True, null=True)
    message_time = models.DateTimeField(auto_now_add=True)
    reciever_id = models.IntegerField(blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.sender_id}'
    
    

class UserProfileModel(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    name = models.CharField(blank=True, null=True, max_length=100)
    online_status = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.user.username


class ChatModel(models.Model):
    sender = models.CharField(max_length=100, default=None)
    message = models.TextField(null=True, blank=True)
    thread_name = models.CharField(null=True, blank=True, max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.message
    
class ChatNotification(models.Model):
    chat = models.ForeignKey(to=ChatModel, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    is_seen = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.user.id
    
    




class ChatGroup(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name='chatgroups')
    created_at = models.DateTimeField(auto_now_add=True)

class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='group_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)