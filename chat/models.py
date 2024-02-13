from django.db import models

# Create your models here.
class TmpMsg(models.Model):
    user_id = models.CharField(max_length=50,primary_key=True)
    count = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    body = models.TextField()
    question = models.TextField()
    chat_type = models.IntegerField(default=1)
    body_payload = models.TextField()
    question_payload = models.TextField()


class ChatType(models.Model):
    group_name = models.CharField(max_length=100)
    password = models.CharField(max_length=50)
    initial_text = models.TextField()
    second_text = models.TextField()
    initial_question = models.TextField()
    second_question = models.TextField()
    text_model = models.PositiveSmallIntegerField(default=3)
    question_model = models.PositiveSmallIntegerField(default=4)
    release = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id}: {self.group_name}"