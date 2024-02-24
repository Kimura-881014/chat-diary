from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from urllib.parse import urlencode


# Create your views here.
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.contrib.auth.hashers import check_password
from .models import Data
from chat.models import ChatType
from accounts.models import User
from .forms import EditForm, MailForm

import os
from pathlib import Path
from dotenv import load_dotenv

from django.db.models import Q
from django.contrib import messages
from django.core.mail import send_mail

BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path)

class LoginView(TemplateView):
    def get(self, request,*args, **kwargs):
        user_id = request.GET.get('id')
        password = request.GET.get('pw')
        user = authenticate(username=user_id, password=password)
        
        if user is not None:
            login(self.request, user)
            return redirect('top_page')
        else:
            return render(request, 'error.html')


class IndexView(LoginRequiredMixin,TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        user_id = self.request.user.user_id
        context = super().get_context_data(**kwargs)
        if 'page' in self.request.GET:
            page = int(self.request.GET.get('page'))
        else:
            page = 1

        if 'search' in self.request.GET:
            search_word = self.request.GET.get('search')
            release = self.request.GET.get('release')
            if release=="True":
                print('True')
                data = Data.objects.filter(Q(title__contains = search_word) | Q(body__contains = search_word),release=True).order_by('posted_date').reverse()
            else:
                print('False')
                data = Data.objects.filter(Q(title__contains = search_word) | Q(body__contains = search_word),user_id=User.objects.get(user_id=user_id)).order_by('posted_date').reverse()
            url = "&search="+search_word+"&release="+release
        else:
            data = Data.objects.filter(user_id=User.objects.get(user_id=user_id)).order_by('posted_date').reverse()
            url = ""
        data_page = Paginator(data, 1)
        data_p = data_page.get_page(page)
        data_list = data_p.paginator.get_elided_page_range(page)
        context['data_p'] = data_p
        context['data_list'] = data_list
        context['page_url_para'] = url
        context['id'] = user_id

        return context
    


class DetailView(LoginRequiredMixin,TemplateView):
    template_name = 'detail.html'

    def get_context_data(self, index, *args, **kwargs):
        user_id = self.request.user.user_id
        context = super().get_context_data(**kwargs)
        # user_id = (self.request.GET.get('id'))
        # index = int(self.request.GET.get('index'))
        col = Data.objects.get(id=index)
        if col.user.user_id == user_id: # 見ようとしているcolのuseridがgetのidと等しいとき
            context['data'] = col
            context['id'] = user_id
            context['row'] = len(col.body)/40 + 3
            context['editable'] = True
            return context
        elif col.release == True:
            context['data'] = col
            context['id'] = user_id
            context['row'] = len(col.body)/40 + 3
            context['editable'] = False
            return context

        else: # 不正アクセス　ここ
           template_name = 'error.html'



class EditView(LoginRequiredMixin,TemplateView):
    template_name = 'edit.html'
    # アクセスしてきたときにhtmlと入力フォームを返す
    def get_context_data(self, index, *args, **kwargs):
        user = self.request.user.user_id
        context = super().get_context_data(**kwargs)
        col = Data.objects.get(id=index)
        if col.user == user: # 修正するcolのuseridがgetのidと等しいとき
            print("here")
            initial = {'user':col.user,
                       'title':col.title,
                       'posted_date':col.posted_date,
                       'body': col.body,
                       'chat_type':col.chat_type,
                       'release':col.release}
            form = EditForm(initial=initial)
            context['data'] = col
            # context['id'] = user_id
            context['form'] = form
            return context
        else: # 不正アクセス ここ
            template_name = 'error.html'


######### form['user'] == self.request.user####################
    # editpageで修正ボタンが押されてPOST requestが飛んできたとき
    def post(self, request, index, *args, **kwargs):
        user = self.request.user
        col = Data.objects.get(id=index)
        if col.user == user:
            form = EditForm(request.POST)
            if form.is_valid():
                title = form.cleaned_data['title']
                body = form.cleaned_data['body']
                posted_date = form.cleaned_data['posted_date']
                release = form.cleaned_data['release']

                col.title = title
                col.body = body
                col.posted_date = posted_date
                col.release = release
                col.save()

                return redirect("detail_page",index=index)
        # else: # 不正削除
        return render(request, 'error.html')
    
class MyDeleteView(LoginRequiredMixin,TemplateView):
    def get(self, request, index, *args, **kwargs):
        user_id = self.request.user.user_id
        # user_id = (self.request.GET.get('id'))
        # index = int(self.request.GET.get('index'))
        col = Data.objects.get(id=index)
        if col.user.user_id == user_id: # 消そうとしているcolのuseridがgetのidと等しいとき
            col.delete()
            url = reverse('top_page')
            parameters = urlencode({'page':1})
            # parameters = urlencode({'id':user_id,'page':1})
            return redirect(f'{url}?{parameters}')
        else: # 不正削除
           return render(request, 'error.html')
        



class ChatTypeView(LoginRequiredMixin,TemplateView):
    template_name = 'chat-type.html'
    # アクセスしてきたときにhtmlと入力フォームを返す
    def get_context_data(self, *args, **kwargs):
        user_id = self.request.user.user_id
        context = super().get_context_data(**kwargs)
        col = User.objects.get(user_id=user_id)
        chat_type_number_list = eval(col.chat_type)
        chat_type_query_list = list(ChatType.objects.filter(id__in=chat_type_number_list).values('id','group_name'))
        context['my_chat_type'] = chat_type_query_list
        context['release_chat_type'] = ChatType.objects.filter(~Q(id__in=chat_type_number_list),release=True)
        return context

    
    # 送信ボタンが押されてPOST requestが飛んできたとき
    def post(self, request, *args, **kwargs):
        chat_list = request.POST.getlist('check[]')
        if request.POST.get('no-release-pw') != "":
            group_name = request.POST.get('no-release-name')
            password = request.POST.get('no-release-pw')
            col = ChatType.objects.get(group_name=group_name)
            if check_password(password,col.password):
                chat_list.append(str(col.id))
            else:
                messages.add_message(request, messages.WARNING, "パスワードが違います")
        if len(chat_list) < 14:
            user_id = self.request.user.user_id
            col = User.objects.get(user_id=user_id)
            col.chat_type = str(chat_list)
            col.save()
            messages.add_message(request, messages.SUCCESS, "登録されました")
            return redirect("chat_type")
        else:
            messages.add_message(request, messages.ERROR, "14個以上は登録できません")
            return redirect("chat_type")
        


class MailView(LoginRequiredMixin,TemplateView):
    template_name = 'mail.html'
    # アクセスしてきたときにhtmlと入力フォームを返す
    def get_context_data(self, *args, **kwargs):
        user_id = self.request.user.user_id
        form = MailForm()
        context = super().get_context_data(**kwargs)
        context['form'] = form
        return context

    
    # 送信ボタンが押されてPOST requestが飛んできたとき
    def post(self, request, *args, **kwargs):
        form = MailForm(request.POST)
        if form.is_valid():
            sender = form.cleaned_data['sender']
            message = form.cleaned_data['message']
            anonymas = form.cleaned_data['anonymas']
            title = "【chat-diary】"
            if anonymas == False:
                title = title + str(self.request.user.user_id)+"さんからのコメント"
            message = message + '\n\n返信先:' + str(sender)
            send_mail(title,message,sender,[os.environ['EMAIL_HOST_USER'],os.environ['EMAIL_STUFF_USER']],fail_silently=False)
            # send_mail(title,message,sender,[os.environ['EMAIL_STUFF_USER']],fail_silently=False)
            return redirect("top_page")
        else: # 不正削除
           return render(request, 'error.html')

        # return redirect("chat_type")