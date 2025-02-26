from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('add-task/', views.add_task, name='add_task'),
    path('update-task/<int:task_id>/', views.update_task, name='update_task'),  
    path('delete-task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
]
