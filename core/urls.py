from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('chat/<int:receiver_pk>/', views.ChatView.as_view(), name='chat'),
]