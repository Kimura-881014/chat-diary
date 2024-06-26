import base64, hmac, hashlib
import time

import random, string
import os
from pathlib import Path
from dotenv import load_dotenv

from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy


from django.http import HttpResponse
import urllib.request
import json
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.mixins import LoginRequiredMixin


from .models import TmpMsg, ChatType
from diary.models import Data
from accounts.models import User


import openai
import anthropic

from .forms import SetPasswordForm

import boto3
from PIL import Image, ImageOps
from io import BytesIO

# Create your views here.
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.utils.translation import gettext as _
from django.contrib.auth.hashers import make_password

class IndexView(TemplateView):
    template_name = 'test.html'


week_max_number_of_times = 100
BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path)
openai.api_key = os.environ['OPENAI_API_KEY']

diary_url = os.environ['DIARY_URL']


REPLY_ENDPOINT_URL = "https://api.line.me/v2/bot/message/reply"
DOWNLOAD_URL = 'https://api-data.line.me/v2/bot/message/{messageId}/content'
ACCESSTOKEN = os.environ['ACCESSTOKEN']
CHANNEL_SECRET = os.environ['CHANNEL_SECRET']
HEADER = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + ACCESSTOKEN
}

s3 = boto3.client('s3',
                   aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                   aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                   region_name='ap-northeast-1')

client = anthropic.Anthropic(
    # もし環境変数でAPIキーをセットできなければここで指定:
    # api_key="..."
)

BUCKET_NAME = os.environ['BUCKET_NAME']


@csrf_exempt
def call_back(request):
    if request.method == 'POST':
        # 署名を検証
        hash = hmac.new(CHANNEL_SECRET.encode('utf-8'),
            request.body, hashlib.sha256).digest()
        signature = base64.b64encode(hash)
        x_line_signature = request.headers['x-line-signature'].encode()
        if signature == x_line_signature:
            request = json.loads(request.body.decode('utf-8'))
            data = request['events'][0]
            reply_token = data['replyToken']
            user_id = data['source']['userId']
            if data['type'] == 'message':
                message = data['message']
                if message['type'] == 'text':
                    line_message = LineMessage(create_text_message(message['text'],user_id,request))
                    line_message.reply(reply_token)
                elif message['type'] == 'image':
                    print('ok')
                    MessageId = message['id']
                    line_message = LineMessage(save_image_to_s3(MessageId,user_id))
                    line_message.reply(reply_token)

            elif data['type'] == 'postback':
                message = data['postback']
                line_message = LineMessage(return_post_back(message['data'],user_id))
                line_message.reply(reply_token)
        return HttpResponse(status=200)


def save_image_to_s3(message_id,user_id):
    download_url = DOWNLOAD_URL.format(messageId=message_id)

    # LINEから画像をダウンロード
    request = urllib.request.Request(download_url, headers=HEADER)
    response = urllib.request.urlopen(request)
    image_data = response.read()
    image_data_resize = resize_with_padding(image_data, 320, 180)

    # S3に画像をアップロード
    file_path = message_id + '.jpg'
    s3.put_object(Bucket=BUCKET_NAME, Key=file_path, Body=image_data_resize, ContentType="image/jpeg")

    try:
        col = TmpMsg.objects.get(user__user_id=user_id)

    except (TmpMsg.DoesNotExist,User.DoesNotExist):
        col = NewChatMember(user_id)
        ## ここでTmpMsgを作成する。。
        ## 下のsaveができないから考える。
    
    if col.image_key != "":
        s3.delete_object(Bucket=BUCKET_NAME, Key=col.image_key)
    
    col.image_key = file_path
    col.save()

    message = [{'type': 'text','text': '画像を保存しました'}]

    return message


def create_text_message(message,user_id,request):
    if message == '保存':
        message = save_data(user_id)

    elif message == '日記を見る':
        message = send_diary_url(user_id,request)

    elif message == 'チャットタイプを変更':
        message = send_chat_type(user_id)

    elif message == 'テスト':
        message = [{'type': 'text','text': 'test1'},
                   {'type': 'text',
                    'text': 'test2',"quickReply": {
    "items": [
    {
        "type": "action",
        "action": {
                    "type": "message",
                    "label": "日記を見る",
                    "text": "日記を見る"
                    }
    },
    {
        "type": "action",
        "action": {
                    "type": "message",
                    "label": "保存する",
                    "text": "保存"
                    }
    },
    {
        "type": "action",
        "action": {
                    "type": "message",
                    "label": "違う答えをつくる",
                    "text": "やり直し"
                    }
    }
    ]
    }}]
    
    else:
        message = gpt_chat(user_id,message)
    return message


# TmpMsgをDataに保存して初期化する関数
def save_data(user_id):
    try:
        user = User.objects.get(user_id=user_id)
        col = TmpMsg.objects.get(user=user)
    except (User.DoesNotExist,TmpMsg.DoesNotExist):
        message = [{'type': 'text','text': '保存データがありません'}]
        message = add_quick_replay_see_diary(message)
        return message
    if col.title != "":
        Data.objects.create(user=user,title=col.title,body=col.body,chat_type=col.chat_type,image_key=col.image_key)
        TmpMsg.objects.update_or_create(user=user,
                                                defaults={
                                                            'title':"",
                                                            'question':"",
                                                            'body':"",
                                                            'image_key':"../static/image/book.png",
                                                            'chat_type':col.chat_type,
                                                            'body_payload':"",
                                                            'question_payload':""
                                                        })
        message = [{'type': 'text','text': '保存しました'}]      
    else:
        message = [{'type': 'text','text': '保存データがありません'}]

    message = add_quick_replay_see_diary(message)
    return message

# サイトURLを送る
def send_diary_url(user_id,request):
    try:
        password = randompwd(20)
        u = User.objects.get(user_id=user_id)
        u.set_password(password)
        u.save()
        url = diary_url +str(reverse('login_page'))+"?id="+user_id+"&pw="+password+"&page=1&openExternalBrowser=1" 
        message = [{'type': 'text','text': "下のボタンを押してください",
                        "quickReply": {"items": [{"type": "action",
                                                "action": {"type": "uri",
                                                            "label": "ここをクリック",
                                                            "uri": url}},
                                                {"type": "action",
                                                "action": {"type": "message",
                                                    "label": "チャットタイプを変更",
                                                    "text": "チャットタイプを変更"}}
                                                            ]}}]
    except User.DoesNotExist:
        message = [{'type': 'text','text': '保存データがありません*1'}]
        message = add_quick_replay_see_diary(message)

    return message

# チャンネルを13個以上入るとクイックリプライで送信できないため13個以上のエラー処理を書く
def send_chat_type(user_id):
    col = User.objects.get(user_id=user_id)
    now_chat_type = TmpMsg.objects.get(user=col).chat_type.id
    chat_type_number_list = eval(col.chat_type)
    chat_type_query_list = list(ChatType.objects.filter(id__in=chat_type_number_list).values('id','group_name'))

    action_list = []
    for i in chat_type_query_list:
        id = i['id']
        group_name = i['group_name']
        
        if id == now_chat_type:
            now_chat_type_name = group_name
        
        action_list.append({"type":"action","action":{"type":"postback","label":group_name,
                                                      "data":"chabge_chat_type_to_"+str(id)+"_"+group_name,"displayText":group_name+"に変更"}})
    try:
        now_chat_type_name
    except NameError:
        now_chat_type_name = "過去に登録されていたチャットタイプ"
    message = [{'type': 'text','text': "現在のチャットタイプは"+str(now_chat_type_name)+"です。\n以下から選択してください。"}]

    message[-1]['quickReply'] = {"items":action_list}

    return message



def gpt_chat(user_id,message):
    try:
        col = TmpMsg.objects.get(user__user_id=user_id)
        # col = TmpMsg.objects.get(user=User.objects.get(user_id=user_id))

    except (TmpMsg.DoesNotExist,User.DoesNotExist):
        col = NewChatMember(user_id)
    
    if col.count > week_max_number_of_times:
        message = [{'type': 'text','text': '使用制限を超えています'}]
        message = add_quick_replay_see_diary(message)
        return message
    
    else:
        # answer1 --> 文章
        # answer2 --> 質問
        if message == 'やり直し':
            if col.body_payload == "":
                if col.question_payload == "":
                    message = [{'type': 'text','text': '会話履歴がありません'}]
                    message = add_quick_replay_see_diary(message)
                    return message
                answer2 = re_chat_api(col.question_payload)
                defaults={
                            'count':col.count+1,
                            'question':answer2,
                            # 'chat_type':col.chat_type,
                        }
                message = [{'type': 'text','text': answer2}]
            else:
                answer1 = re_chat_api(col.body_payload)
                answer2 = re_chat_api(col.question_payload)
                defaults={
                            'count':col.count+1,
                            'question':answer2,
                            'body':answer1,
                            # 'chat_type':col.chat_type,
                        }
                message = [{'type': 'text','text': answer1},
                           {'type': 'text','text': answer2}]

        else:
            if col.question == "":
                answer2, payload2 = chat_api("q",3,message,col)
                defaults={
                            'count':col.count+1,
                            'title':message,
                            'question':answer2,
                            # 'chat_type':col.chat_type,
                            'question_payload':payload2,
                        }
                message = [{'type': 'text','text': answer2}]
            elif col.body == "":
                answer1, payload1 = chat_api("t",1,message,col)
                answer2, payload2 = chat_api("q",4,answer1,col)
                defaults={
                            'count':col.count+1,
                            'question':answer2,
                            'body':answer1,
                            # 'chat_type':col.chat_type,
                            'question_payload':payload2,
                            'body_payload':payload1,
                        }
                message = [{'type': 'text','text': answer1},
                           {'type': 'text','text': answer2}]
            else:
                answer1,payload1 = chat_api("t",2,message,col)
                answer2,payload2 = chat_api("q",4,answer1,col)
                defaults={
                            'count':col.count+1,
                            'question':answer2,
                            'body':answer1,
                            # 'chat_type':col.chat_type,
                            'question_payload':payload2,
                            'body_payload':payload1,
                        }
                message = [{'type': 'text','text': answer1},
                           {'type': 'text','text': answer2}]

        
        TmpMsg.objects.update_or_create(user=col.user,
                                            defaults=defaults)
        # message = [{'type': 'text','text': gpt_api(3,5,message,col)}]
        message = add_quick_replay(message)
        return message



# GPT, cloude3のAPIをたたく
def chat_api(t_or_q,prompt,text,data):
    # model = select_model(model)
    # prompt = select_prompt(prompt)
    property = ChatAPIProperty(data.chat_type.id)
    property.select_model(t_or_q)
    property.select_prompt(prompt,text,data)
    if "gpt" in property.model:
        messages = [
                    {"role": "system", "content": property.prompt},
                    {"role": "user", "content": property.text}
                    ]
        # print("--------------------------------")
        # print(messages)
        # print("--------------------------------")
        response = openai.chat.completions.create(
                        model = property.model,
                        messages = messages,
                        temperature=0
                    )
        text = response.choices[0].message.content
    elif "claude" in property.model:
        messages = [
                    {"role": "user", "content": property.text}
                    ]
        response = client.messages.create(
                        model=property.model,
                        max_tokens=1000, # 出力上限（4096まで）
                        temperature=0.0, # 0.0-1.0
                        system=property.prompt, # 必要ならシステムプロンプトを設定
                        messages=messages
                    )
        text = response.content[0].text
        messages.append({"role": "system", "content": property.prompt})

    print(response)
    print("model:",property.model)
    
    messages.append({"model":property.model})
    return text, json.dumps(messages)



# やり直しの時のChat API
def re_chat_api(payload):
    messages = json.loads(payload)
    model = messages.pop(-1)['model']
    # print(messages)
    # print("--------------------------------")
    # start = time.time()
    if "gpt" in model:
        response = openai.chat.completions.create(
                        model = model,
                        messages = messages,
                        temperature=0.7
                    )
        text = response.choices[0].message.content
    elif "claude" in model:
        system = messages.pop(-1)['content']
        response = client.messages.create(
                        model=model,
                        max_tokens=1000, # 出力上限（4096まで）
                        temperature=0.0, # 0.0-1.0
                        system=system, # 必要ならシステムプロンプトを設定
                        messages=messages
                    )
        text = response.content[0].text

    return text


class ChatAPIProperty():
    def __init__(self,id):
        self.col = ChatType.objects.get(id=id)

    def select_model(self,t_or_q):
        if t_or_q == "t":
            self.model = self.col.text_model_s
        else:
            self.model = self.col.question_model_s


    def select_prompt(self,num,text,data):
        if num == 1:
            self.prompt = self.col.initial_text
            self.text = "#User-provided\n"+data.question +"\n"+ text
        elif num == 2:
            self.prompt = self.col.second_text
            self.text = "#User-provided\n"+data.question+"\n"+text+"\n"+"#Daiary"+data.body
        elif num == 3:
            self.prompt = self.col.initial_question
            self.text = text
        elif num == 4:
            self.prompt = self.col.second_question
            # 最後のtextはanswerを使用
            self.text = "#Records\n"+text
        else:
            pass
            # self.prompt = prompt5
            # self.text = "ありがとう"



class LineMessage():
    def __init__(self, messages):
        self.messages = messages

    def reply(self, reply_token):
        body = {
            'replyToken': reply_token,
            'messages': self.messages
        }
        req = urllib.request.Request(REPLY_ENDPOINT_URL, json.dumps(body).encode(), HEADER)
        try:
            with urllib.request.urlopen(req) as res:
                body = res.read()
        except urllib.error.HTTPError as err:
            print(err)
        except urllib.error.URLError as err:
            print(err.reason)




class NewChatMember():
    def __init__(self,user_id):
        self.count = 0
        self.title = ""
        self.body = ""
        self.chat_type = ChatType.objects.get(id=1)
        self.question = ""
        self.body_payload = ""
        self.question_payload = ""
        self.image_key = "../static/image/book.png"
        password = randompwd(20)
        user = User.objects.create_user(user_id,"", password)
        user.save()
        self.user = user



def add_quick_replay_see_diary(message):
    message[-1]['quickReply'] = {"items": [{"type": "action",
                                        "action": {"type": "message",
                                                    "label": "日記を見る",
                                                    "text": "日記を見る"}},
                                            {"type": "action",
                                        "action": {"type": "message",
                                                    "label": "チャットタイプを変更",
                                                    "text": "チャットタイプを変更"}}]}
    return message


def add_quick_replay(message):
    message[-1]['quickReply'] = {"items": [{"type": "action",
                                        "action": {"type": "message",
                                                    "label": "日記を見る",
                                                    "text": "日記を見る"}},
                                           {"type": "action",
                                        "action": {"type": "message",
                                                    "label": "保存する",
                                                    "text": "保存"}},
                                           {"type": "action",
                                        "action": {"type": "message",
                                                    "label": "違う答えをつくる",
                                                    "text": "やり直し"}},
                                           {"type": "action",
                                        "action": {"type": "message",
                                                    "label": "チャットタイプを変更",
                                                    "text": "チャットタイプを変更"}}]}
    return message


def randompwd(n):
   return ''.join(random.choices(string.ascii_letters + string.digits, k=n))


# 新規ユーザが最初にchat_type_changeできないからしたいね
def return_post_back(message,user_id):
    if message.startswith('chabge_chat_type_to_'):
        message_split = message.split('_')
        id = message_split[-2]
        group_name = message_split[-1]
        try:
            col = TmpMsg.objects.get(user=User.objects.get(user_id=user_id))
            col.chat_type = ChatType.objects.get(id=id)
            col.save()
        except TmpMsg.DoesNotExist:
            # col = NewChatMember(user_id)
            message = [{'type': 'text','text': '申し訳ありません一度normalで会話してくださいに変更しました。'}]
            return message
        message = [{'type': 'text','text': group_name+'に変更しました。'}]
        message = add_quick_replay_see_diary(message)
    else:
        message = [{'type': 'text','text': 'error in change_chat_type'}]
    return message


# 画像を小さくする関数
def resize_with_padding(bytes_data, width, height):
    # Bytesデータから画像を読み込む
    image = Image.open(BytesIO(bytes_data))
    
    # 縦横比を維持しながら指定されたサイズにリサイズする
    resized_image = ImageOps.pad(image, (width, height), color='white')
    
    # リサイズ後の画像のbytesデータを取得
    resized_bytes = BytesIO()
    resized_image.save(resized_bytes, format=image.format)
    resized_bytes.seek(0)
    
    return resized_bytes.getvalue()




# adminサイトのChatTypeパスワード変更
class PasswordContextMixin:
    extra_context = None
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"title": self.title, **(self.extra_context or {})})
        return context
        

class PasswordResetView(FormView):
    template_name = 'my_password_change_form.html'
    form_class = SetPasswordForm
    success_url = reverse_lazy('password_change_done')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['index'] = self.kwargs['index']  # Assuming you pass 'index' as a parameter in the URL
        return kwargs

    def form_valid(self, form):
        index = form.index  # Access the index from the form
        # You can perform any additional processing or validation here if needed
        # For example, you can update the user's password and log them in
        col = ChatType.objects.get(id=index)
        col.password = make_password(form.cleaned_data['new_password1'])
        col.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        # Handle invalid form submission here if needed
        return super().form_invalid(form)
    

class PasswordChangeDoneView(PasswordContextMixin, TemplateView):
    template_name = "my_password_change_done.html"
    title = _("Password change successful")