from django.urls import path
from .views import ChatbotAPIView

urlpatterns = [
    path('bot/', ChatbotAPIView.as_view(), name='chatbot'),
]
