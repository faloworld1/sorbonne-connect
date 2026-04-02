from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.ConnexionView.as_view(), name='login'),
    path('logout/', views.DeconnexionView.as_view(), name='logout'),
    path('register/', views.inscription, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profil/', views.profil, name='profil'),
]
