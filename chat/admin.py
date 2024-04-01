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
        (None, {'fields':('password','initial_text','second_text','initial_question','second_question',),'description':'id'}),
        (None, {'fields':('text_model_s','question_model_s','release')})
    ]

    def get_object(self, request, view, object_id):
        obj = super(ChatTypeAdmin, self).get_object(request,view, object_id)
        if obj:
            url = reverse('change_password', args=[obj.id])
            # objが存在する場合、そのidを設定します
            gpt_url = "https://platform.openai.com/docs/models/overview"
            claude_url = "https://github.com/anthropics/anthropic-sdk-typescript/blob/a974f6cc5f7e3cc5f2363966e60e03285c2b6d66/src/resources/messages.ts#L530"
            self.fieldsets[1][1]['description'] = '生のパスワードは格納されていないため、このパスワードを確認する方法はありません。しかし'+f'<a href="{url}">このフォーム</a>'+'を使用してパスワードを変更できます。'
            self.fieldsets[2][1]['description'] = '<li>Chat GPTのmodelは'+f'<a href="{gpt_url}">こちら</a></li>'+'<li>Claudeのmodelは'+f'<a href="{claude_url}">こちら</a></li>'
        return obj

# Register your models here.
admin.site.register(TmpMsg)
admin.site.register(ChatType, ChatTypeAdmin)

