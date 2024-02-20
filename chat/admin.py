# from django.contrib import admin
# from chat.models import TmpMsg, ChatType
# from .forms import ChatTypeForm

# class ChatTypeAdmin(admin.ModelAdmin):
#     readonly_fields = ('password',)
#     form = ChatTypeForm
#     fieldsets = [
#         (None, {'fields':('group_name','password'),'description':id})
#     ]


# # Register your models here.
# admin.site.register(TmpMsg)
# admin.site.register(ChatType,ChatTypeAdmin)


from django.urls import reverse
from urllib.parse import urlencode
from django.contrib import admin
from chat.models import TmpMsg, ChatType
from .forms import ChatTypeForm

class ChatTypeAdmin(admin.ModelAdmin):
    readonly_fields = ('password',)
    form = ChatTypeForm
    fieldsets = [
        (None, {'fields':('group_name',)}),
        (None, {'fields':('password','initial_text','second_text','initial_question','second_question',
                          'text_model','question_model','release'),'description':'id'})
    ]

    def get_object(self, request, view, object_id):
        obj = super(ChatTypeAdmin, self).get_object(request,view, object_id)
        if obj:
            url = reverse('change_password', args=[obj.id])
            # objが存在する場合、そのidを設定します
            self.fieldsets[1][1]['description'] = '生のパスワードは格納されていないため、このパスワードを確認する方法はありません。しかし'+f'<a href="{url}">このフォーム</a>'+'を使用してパスワードを変更できます。'
        return obj

# Register your models here.
admin.site.register(TmpMsg)
admin.site.register(ChatType, ChatTypeAdmin)

