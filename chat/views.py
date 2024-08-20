from rest_framework.decorators import api_view, authentication_classes, permission_classes
from .serailizers import UserGetSerializer, ChatSerializer
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from accounts.tokenauthentication import JWTAuthentication
from chat.models import Chat
from .models import ChatGroup, GroupMessage
from .serailizers import GroupSerializer, GroupMessageSerializer
import time

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404

# Create your views here.

User = get_user_model()

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 30

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_user_list(request):
    time.sleep(1)
    if request.method == 'GET':
        try:
            user_obj = User.objects.exclude(id=request.user.id)
            seralizer = UserGetSerializer(user_obj, many=True)
            return Response(seralizer.data)
        except Exception as e:
            print(e)
            return Response(seralizer.errors)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_chat_list(request, opponent_id):
    if request.method == 'GET':
        try:
            # time.sleep(4)
            user_ids = [int(request.user.id), int(opponent_id)]
            user_ids = sorted(user_ids)
            thread_name = f"chat_{user_ids[0]}-{user_ids[1]}"
            chats = Chat.objects.filter(thread_name=thread_name).order_by('message_time')
            # paginator = CustomPagination()
            # results = paginator.paginate_queryset(chats, request)
            serializer = ChatSerializer(chats, context={
                'request': request
            }, many=True)
            user_obj = User.objects.get(id=opponent_id)
            # print(serializer.data,"================messagesss================")
            # return paginator.get_paginated_response(serializer.data)
            data={"messages": serializer.data,"username": user_obj.first_name if user_obj.first_name!='' else user_obj.email}
            return Response(data)
        except Exception as e:
            print(e)
            return Response({},status=400)
        



# class GroupViewSet(ModelViewSet):
#     queryset = ChatGroup.objects.all()
#     serializer_class = GroupSerializer
#     permission_classes = [IsAuthenticated]
    
#     def list(self, request, *args, **kwargs):
#         print("List----------------")
#         return super().list(request, *args, **kwargs)
    
#     def create(self, request, *args, **kwargs):
#         print("Creating")
#         return super().create(request, *args, **kwargs)

# class GroupMessageViewSet(ModelViewSet):
#     queryset = GroupMessage.objects.all()
#     serializer_class = GroupMessageSerializer
#     permission_classes = [IsAuthenticated]


class GroupAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, format=None):
        print(pk,"-------[kuser---------------",request.user.id)
        if pk:
            group = ChatGroup.objects.get(pk=pk,members__in=[request.user.id])
            # group = get_object_or_404(ChatGroup, pk=pk)
            serializer = GroupSerializer(group, context={
                'request': request
            })
        else:
            groups = ChatGroup.objects.filter(members__in=[request.user.id])
            serializer = GroupSerializer(groups, context={
                'request': request
            }, many=True)
        # print(serializer.data,"---------------mesage group--")
        return Response(serializer.data)

    def post(self, request, format=None):
        group_data=request.data
        members=group_data['members']
        members.append(request.user.id)
        # print(dataa,"--------------------------------")
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    def put(self, request, pk, format=None):
        group = get_object_or_404(ChatGroup, pk=pk)
        serializer = GroupSerializer(group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    def delete(self, request, pk, format=None):
        group = get_object_or_404(ChatGroup, pk=pk)
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class GroupMessageAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk=None, format=None):
        if pk:
            message = get_object_or_404(GroupMessage, pk=pk)
            serializer = GroupMessageSerializer(message)
        else:
            messages = GroupMessage.objects.all()
            serializer = GroupMessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = GroupMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        message = get_object_or_404(GroupMessage, pk=pk)
        serializer = GroupMessageSerializer(message, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        message = get_object_or_404(GroupMessage, pk=pk)
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
