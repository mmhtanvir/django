from django.contrib import admin
from django.urls import path
from users import views

urlpatterns = [
    path('', views.users, name='users'),
    path('update_user/<id>', views.update_user, name='update_user'),
    path('delete_user/<id>', views.delete_user, name='delete_user'),
    path('delete_user/<id>', views.delete_user, name='delete_user'),
]