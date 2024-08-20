from django.urls import path,re_path
from .consumer import PersonalChatConsumer,GroupChatConsumer,OnlineStatusConsumer,NotificationConsumer

websocket_urlpatterns=[
    path("ws/chat/<int:id>/",PersonalChatConsumer.as_asgi()),
    path('ws/online/', OnlineStatusConsumer.as_asgi()),
    path('ws/notify/', NotificationConsumer.as_asgi()),
    re_path(r"ws/chat/group/(?P<group_name>\w+)/$", GroupChatConsumer.as_asgi()),
    
]