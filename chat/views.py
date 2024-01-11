from django.shortcuts import render
from django.urls import reverse

# Create your views here.
from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name = 'test.html'




from django.shortcuts import render
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt



@csrf_exempt
def call_back(request):
    if request.method == 'POST':
        request = json.loads(request.body.decode('utf-8'))
        data = request['events'][0]
        message = data['message']
        user_id = data['source']['userId']
        reply_token = data['replyToken']
        line_message = LineMessage(create_template_message(message['text'],user_id))
        line_message.reply(reply_token)
        return HttpResponse(status=200)


def create_template_message(message,user_id):
    if message == '保存':
        message = '保存しました'
    elif message == '日記を見る':
        message = "https://kimura881014.pythonanywhere.com/diary"+str(reverse('top_page', kwargs={'user_id':user_id}))+"?page=1"
    test_message = [
                {
                    'type': 'text',
                    'text': message
                }
            ]
    return test_message


from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import urllib.request
import json

REPLY_ENDPOINT_URL = "https://api.line.me/v2/bot/message/reply"
ACCESSTOKEN = 'nKt2wn0DZcckzq3gOMym/gZsWU9UButcbiW2XBxHAsGJ0ebQ6AmuDcNuWPgMwKN1VUQhAfJEqAhJlveutQHOIQthW9W1E8tUcSf64YmeGGN4yHgtnMniIZ4MgR1DfZzzCbT74odF9U4oNLrFaRccmgdB04t89/1O/w1cDnyilFU='
HEADER = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + ACCESSTOKEN
}

class LineMessage():
    def __init__(self, messages):
        self.messages = messages

    def reply(self, reply_token):
        body = {
            'replyToken': reply_token,
            'messages': self.messages
        }
        print(body)
        req = urllib.request.Request(REPLY_ENDPOINT_URL, json.dumps(body).encode(), HEADER)
        try:
            with urllib.request.urlopen(req) as res:
                body = res.read()
        except urllib.error.HTTPError as err:
            print(err)
        except urllib.error.URLError as err:
            print(err.reason)
