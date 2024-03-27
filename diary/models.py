from django.db import models
from django.utils import timezone
from chat.models import ChatType
from accounts.models import User

# Create your models here.
class Data(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    posted_date = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=255)
    body = models.TextField()
    image_url = models.CharField(max_length=100, default="../static/image/book.png")
    chat_type = models.ForeignKey(ChatType,on_delete=models.RESTRICT)
    release = models.BooleanField(default=False)