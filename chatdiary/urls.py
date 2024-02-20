"""chatdiary URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path, include
from chat.views import PasswordChangeDoneView, PasswordResetView

urlpatterns = [
    path('admin/chat/chattype/<int:index>/password/', PasswordResetView.as_view(),name="change_password"),
    path('admin/chat/chattype/password_changed/', PasswordChangeDoneView.as_view(),name="password_change_done"),
    path('admin/', admin.site.urls),
    path('chat/',include('chat.urls')),
    path('diary/', include('diary.urls')),
]
