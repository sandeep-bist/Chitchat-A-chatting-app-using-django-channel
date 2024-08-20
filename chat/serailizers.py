from django.contrib.auth import get_user_model
from chat.models import Chat
from rest_framework import serializers
from .models import ChatGroup, GroupMessage
from django.contrib.auth import get_user_model
User=get_user_model()
class UserGetSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = get_user_model()
        fields = ['email', 'first_name', 'last_name', 'id']
        extra_kwargs = {'id': {'read_only': True}}

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = "__all__"
        extra_kwargs = {'id': {'read_only': True}}
    

    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if request := self.context.get('request', None):
            user=request.user
        representation['sender'] = instance.sender_id ==user.id
        return representation

class GroupMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMessage
        fields = ['id', 'group', 'user', 'timestamp']
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if request := self.context.get('request', None):
            user=request.user
        representation['sender'] = instance.user.id ==user.id
        representation['message'] = instance.content
        representation['sender_name'] = f'{instance.user.first_name} {instance.user.last_name}'
        representation['sender_email'] = instance.user.email
        return representation

class GroupSerializer(serializers.ModelSerializer):
    messages = GroupMessageSerializer(many=True, read_only=True)
    class Meta:
        model = ChatGroup
        fields = ['id', 'name', 'members', 'created_at','messages']
    
    def create(self, validated_data):
        group_id = validated_data['name']
        user_id = validated_data['members']
        group,_ = ChatGroup.objects.get_or_create(name=group_id)
        group.members.set(user_id)
        group.save()
        return group


    def to_representation(self, instance):
        # Pass the request to the GroupMessageSerializer
        self.fields['messages'].context['request'] = self.context.get('request')
        return super().to_representation(instance)