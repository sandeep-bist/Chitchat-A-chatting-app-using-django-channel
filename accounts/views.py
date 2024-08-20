from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status,mixins
from rest_framework.generics import GenericAPIView

from accounts.tokenauthentication import JWTAuthentication
from .serailizers import UserSerializer,LoginSerializer
from django.contrib.auth import get_user_model

User=get_user_model()

@api_view(['POST','GET'])
def register_user(request):
    print(request.data,"user data requested")
    serializer=UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,status=200)
    return Response(serializer.errors,status=400)
        

@api_view(['POST'])
def login(request):
    print("request.data-----------",request.data)
    serializer=LoginSerializer(data=request.data)
    if serializer.is_valid():
        token=JWTAuthentication.generate_token(payload=serializer.data)
        return Response({
                         "message":"Login Successfully",
                         "token":token,
                         'user':serializer.data
                         },status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors,status.HTTP_400_BAD_REQUEST)
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def hello(request):
    print("hello there")
    return Response({"message":"hello every one"},status=200)

# class RetrieveCreate(mixins.RetrieveModelMixin, mixins.CreateModelMixin, GenericAPIView):

#     serializer_class = UserSerializer
#     queryset = User.objects.get(id=1)

#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)