from django.urls import path
from .views import register, user_profile, login, login_status

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('profile/', user_profile, name='user-profile'),
    path('login_status/', login_status, name='login_status'),
]