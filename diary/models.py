from django.db import models

# Create your models here.
class Data(models.Model):
    user_id = models.CharField(max_length=50)
    posted_date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    body = models.TextField()
    chat_type = models.SmallIntegerField()
    release = models.BooleanField(default=False)