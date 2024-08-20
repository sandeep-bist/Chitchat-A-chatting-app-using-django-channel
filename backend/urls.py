"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from accounts.views import register_user,login,hello
from chat.views import get_user_list,get_chat_list


urlpatterns = [
    # path('accounts/', include('django.contrib.auth.urls')),
    path('api/', include('chat.urls')),
    path('admin/', admin.site.urls),
    path('register/',register_user,name='register'),
    path('login/',login,name='login'),
    path('hello/',hello,name='hello'),
    
    path('api/users/',get_user_list,name='user_list'),
    path('api/chat/<int:opponent_id>/', get_chat_list, name="chats")
]
