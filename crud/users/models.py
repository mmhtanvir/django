from django.db import models
from django.contrib.auth.models import User
class Users(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.TextField()
    user_image = models.ImageField(upload_to="user-image")