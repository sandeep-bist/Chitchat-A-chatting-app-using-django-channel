import json

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfileModel, ChatNotification
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

User=get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        user_profile=UserProfileModel.objects.create(user=instance,name=instance.first_name,online_status=True)
        user_profile.save()


@receiver(post_save, sender=ChatNotification)
def send_notification(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        notification_obj = ChatNotification.objects.filter(is_seen=False, user=instance.user).count()
        user_id = str(instance.user.id)
        data = {
            'count':notification_obj
        }

        async_to_sync(channel_layer.group_send)(
            user_id, {
                'type':'send_notification',
                'value':json.dumps(data)
            }
        )


@receiver(post_save, sender=UserProfileModel)
def send_onlineStatus(sender, instance, created, **kwargs):
    if not created:
        channel_layer = get_channel_layer()
        user = instance.user.first_name
        user_status = instance.online_status

        data = {
            'username':user,
            'status':user_status
        }
        async_to_sync(channel_layer.group_send)(
            'user', {
                'type':'send_onlineStatus',
                'value':json.dumps(data)
            }
        )