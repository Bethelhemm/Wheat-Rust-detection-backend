# ml_app/urls.py
from django.urls import path
from .views import predict_disease

urlpatterns = [
    path('predict/', predict_disease, name='predict_disease'),
]
