from django.db import models
import mimetypes
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

class Case(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in-progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    category = models.CharField(max_length=100)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    deadline = models.DateTimeField(null=True, blank=True)
    assigned_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_cases')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_cases')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.status}"

class Attachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='case_attachments/')
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField()
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.file and not self.mime_type:
            mime, _ = mimetypes.guess_type(self.file.name)
            self.mime_type = mime or ''
        super().save(*args, **kwargs) 
    
    def __str__(self):
        return self.filename

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.case.title}"

class ActivityLog(models.Model):
    ACTIVITY_TYPES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('status_changed', 'Status Changed'),
        ('priority_changed', 'Priority Changed'),
        ('deadline_changed', 'Deadline Changed'),
        ('assigned', 'Assigned'),
        ('commented', 'Commented'),
        ('attachment_added', 'Attachment Added'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='activity_log')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.activity_type} by {self.user.username} on {self.case.title}"
