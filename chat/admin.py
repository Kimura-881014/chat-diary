from django.contrib import admin
from chat.models import TmpMsg, ChatType

# Register your models here.
admin.site.register(TmpMsg)
admin.site.register(ChatType)
