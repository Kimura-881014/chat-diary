import base64, hmac, hashlib

import random, string
import os
from dotenv import load_dotenv

from django.shortcuts import render
from django.urls import reverse

from django.http import HttpResponse
import urllib.request
import json
from django.views.decorators.csrf import csrf_exempt


from .models import TmpMsg, ChatType
from diary.models import Data
from accounts.models import User


import openai

# Create your views here.
from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name = 'test.html'

# ====================================================
# diary_url = "https://kimura881014.pythonanywhere.com"
diary_url = "https://rested-redbird-widely.ngrok-free.app"
# diary_url = "https://script.google.com/macros/s/AKfycbyS-Xo6rD-_bolhZillBUeGmBt4IcxXPatHc-4dIo_2-saBLnJjZrf4QDO7pjqloqR9/exec"
# ====================================================

week_max_number_of_times = 100
load_dotenv()
openai.api_key = os.environ['OPENAI_API_KEY']

REPLY_ENDPOINT_URL = "https://api.line.me/v2/bot/message/reply"
ACCESSTOKEN = os.environ['ACCESSTOKEN']
CHANNEL_SECRET = os.environ['CHANNEL_SECRET']
HEADER = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + ACCESSTOKEN
}



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
            # print(data)
            if data['type'] == 'message':
                message = data['message']
                if message['type'] == 'text':
                    line_message = LineMessage(create_text_message(message['text'],user_id,request))
                    print("test1",message['text'])
                    line_message.reply(reply_token)
            elif data['type'] == 'postback':
                print(data)
                message = data['postback']
                line_message = LineMessage(return_post_back(message['data'],user_id))
                line_message.reply(reply_token)
        return HttpResponse(status=200)


def create_text_message(message,user_id,request):
    if message == '保存':
        message = save_data(user_id)

    elif message == '日記を見る':
        message = send_diary_url(user_id,request)

    elif message == 'チャットタイプの変更':
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
        col = TmpMsg.objects.get(user_id=user_id)
    except TmpMsg.DoesNotExist:
        message = [{'type': 'text','text': '保存データがありません'}]
        message = add_quick_replay_see_diary(message)
        return message
    if col.title != "":
        Data.objects.create(user_id=user_id,title=col.title,body=col.body,chat_type=col.chat_type)
        TmpMsg.objects.update_or_create(user_id=user_id,
                                                defaults={
                                                            'title':"",
                                                            'question':"",
                                                            'body':"",
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
    password = randompwd(20)
    u = User.objects.get(user_id=user_id)
    u.set_password(password)
    u.save()

    url = diary_url +str(reverse('login_page'))+"?id="+user_id+"&pw="+password+"&page=1&openExternalBrowser=1" 
    # 以下はGASに飛ばす
    # url = diary_url +"?id="+user_id+"&page=1&openExternalBrowser=1"

    message = [{'type': 'text','text': "下のボタンを押してください",
                    "quickReply": {"items": [{"type": "action",
                                            "action": {"type": "uri",
                                                        "label": "ここをクリック",
                                                        "uri": url}}]}}]

    return message

# チャンネルを13個以上入るとクイックリプライで送信できないため13個以上のエラー処理を書く
def send_chat_type(user_id):
    col = User.objects.get(user_id=user_id)
    now_chat_type = TmpMsg.objects.get(user_id=user_id).chat_type
    chat_type_number_list = eval(col.chat_type)
    chat_type_query_list = list(ChatType.objects.filter(id__in=chat_type_number_list).values('id','group_name'))

    action_list = []
    for i in chat_type_query_list:
        id = i['id']
        group_name = i['group_name']
        if id == now_chat_type:
            now_chat_type = group_name
        action_list.append({"type":"action","action":{"type":"postback","label":group_name,
                                                      "data":"chabge_chat_type_to_"+str(id)+"_"+group_name,"displayText":group_name+"に変更"}})
    message = [{'type': 'text','text': "現在のチャットタイプは"+str(now_chat_type)+"です。\n以下から選択してください。"}]

    message[-1]['quickReply'] = {"items":action_list}

    return message



def gpt_chat(user_id,message):
    try:
        col = TmpMsg.objects.get(user_id=user_id)
    except TmpMsg.DoesNotExist:
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
                answer2 = re_gpt("q",col.question_payload,col)
                defaults={
                            'count':col.count+1,
                            'question':answer2,
                            # 'chat_type':col.chat_type,
                        }
                message = [{'type': 'text','text': answer2}]
            else:
                answer1 = re_gpt("t",col.body_payload,col)
                answer2 = re_gpt("q",col.question_payload,col)
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
                answer2, payload2 = gpt_api("q",3,message,col)
                defaults={
                            'count':col.count+1,
                            'title':message,
                            'question':answer2,
                            # 'chat_type':col.chat_type,
                            'question_payload':payload2,
                        }
                message = [{'type': 'text','text': answer2}]
            elif col.body == "":
                answer1, payload1 = gpt_api("t",1,message,col)
                answer2, payload2 = gpt_api("q",4,answer1,col)
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
                answer1,payload1 = gpt_api("t",2,message,col)
                answer2,payload2 = gpt_api("q",4,answer1,col)
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

        
        TmpMsg.objects.update_or_create(user_id=user_id,
                                            defaults=defaults)
        # message = [{'type': 'text','text': gpt_api(3,5,message,col)}]
        message = add_quick_replay(message)
        return message



# GPTのAPIをたたく
def gpt_api(t_or_q,prompt,text,data):
    # model = select_model(model)
    # prompt = select_prompt(prompt)
    propaty = GPTPropaty(data.chat_type)
    propaty.select_model(t_or_q)
    propaty.select_prompt(prompt,text,data)
    messages = [
                {"role": "system", "content": propaty.prompt},
                {"role": "user", "content": propaty.text}
                ]
    print("********************************")
    print(messages)
    print("--------------------------------")
    response = openai.chat.completions.create(
                    model = propaty.model,
                    messages = messages,
                    temperature=0
                )
    text = response.choices[0].message.content
    return text, json.dumps(messages)



# やり直しの時のGPTAPI
def re_gpt(t_or_q,payload,data):
    propaty = GPTPropaty(data.chat_type)
    propaty.select_model(t_or_q)
    messages = json.loads(payload)
    print(messages)
    print("--------------------------------")
    response = openai.chat.completions.create(
                    model = propaty.model,
                    messages = messages,
                    temperature=0.8
                )
    text = response.choices[0].message.content
    return text


class GPTPropaty():
    def __init__(self,id):
        self.col = ChatType.objects.get(id=id)

    def select_model(self,t_or_q):
        if t_or_q == "t":
            model = self.col.text_model
        else:
            model = self.col.question_model
        if model == 3:
            self.model = "gpt-3.5-turbo-1106"
        elif model == 4:
            self.model = "gpt-4-1106-preview"

    def select_prompt(self,num,text,data):
        if num == 1:
            self.prompt = self.col.initial_text
            self.text = data.question +"\n"+ text
        elif num == 2:
            self.prompt = self.col.second_text
            self.text = "#User-provided\n"+data.question+"\n"+text+"\n"+"#Daiary"+data.body
        elif num == 3:
            self.prompt = self.col.initial_question
            self.text = text
        elif num == 4:
            self.prompt = self.col.second_question
            # 最後のtextはanswerを使用
            self.text = text
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
        self.user_id = user_id
        self.count = 0
        self.title = ""
        self.body = ""
        self.chat_type = 1
        self.question = ""
        self.body_payload = ""
        self.que_payload = ""
        password = randompwd(20)
        user = User.objects.create_user(user_id,"", password)
        user.save()



def add_quick_replay_see_diary(message):
    message[-1]['quickReply'] = {"items": [{"type": "action",
                                        "action": {"type": "message",
                                                    "label": "日記を見る",
                                                    "text": "日記を見る"}},
                                            {"type": "action",
                                        "action": {"type": "message",
                                                    "label": "チャットタイプを変更",
                                                    "text": "チャットタイプの変更"}}]}
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
                                                    "text": "チャットタイプの変更"}}]}
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
            col = TmpMsg.objects.get(user_id=user_id)
            col.chat_type = int(id)
            col.save()
        except TmpMsg.DoesNotExist:
            col = NewChatMember(user_id)
            message = [{'type': 'text','text': '申し訳ありません一度normalで会話してくださいに変更しました。'}]
            return message
        message = [{'type': 'text','text': group_name+'に変更しました。'}]
        message = add_quick_replay_see_diary(message)
    else:
        message = [{'type': 'text','text': 'error in change_chat_type'}]
    return message