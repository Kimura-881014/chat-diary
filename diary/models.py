from django.db import models
from django.utils import timezone

# Create your models here.
class Data(models.Model):
    user_id = models.CharField(max_length=50)
    posted_date = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=255)
    body = models.TextField()
    chat_type = models.SmallIntegerField()
    release = models.BooleanField(default=False)