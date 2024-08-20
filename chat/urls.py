from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GroupAPIView, GroupMessageAPIView

# router = DefaultRouter()
# router.register(r'groups-messages', GroupMessageViewSet,"group_messages_list")
# router.register(r'groups', GroupViewSet,"groups_list")

# urlpatterns = [
#     path('', include(router.urls)),
# ]


urlpatterns = [
    path('groups/', GroupAPIView.as_view(), name='group-list-create'),
    path('groups/<int:pk>/', GroupAPIView.as_view(), name='group-detail'),
    path('group-messages/', GroupMessageAPIView.as_view(), name='groupmessage-list-create'),
    path('group-messages/<int:pk>/', GroupMessageAPIView.as_view(), name='groupmessage-detail'),
]