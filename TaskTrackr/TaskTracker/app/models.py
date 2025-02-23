from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Task(models.Model):
    task_name = models.CharField(max_length=255, verbose_name="Task Name")
    due_date = models.DateField(verbose_name="Due Date")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks", verbose_name="Created By")
    status = models.CharField(max_length=50, verbose_name="Status")  
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
    
    def __str__(self):
        return f"{self.task_name} ({self.status})"