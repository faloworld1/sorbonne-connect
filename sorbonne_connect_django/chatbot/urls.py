from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.portal, name='portal'),
    path('chatbot/', views.index, name='index'),
    path('api/send/', views.api_send_message, name='api_send'),
    path('api/satisfaction/', views.api_satisfaction, name='api_satisfaction'),
    path('api/stats/', views.api_stats, name='api_stats'),
    path('api/logs/', views.api_logs, name='api_logs'),
]
