from django.urls import path
from chatbot.views import ChatView

urlpatterns = [
    path('message/', ChatView.as_view(), name='chat'),
]