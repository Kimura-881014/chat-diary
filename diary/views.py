from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from urllib.parse import urlencode


# Create your views here.
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Data
from chat.models import ChatType
from accounts.models import User
from .forms import EditForm

from django.db.models import Q

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
        # user_id = (self.request.GET.get('id'))
        if 'page' in self.request.GET:
            page = int(self.request.GET.get('page'))
        else:
            pass

        if 'search' in self.request.GET:
            search_word = self.request.GET.get('search')
            context['data'] = Data.objects.filter(Q(title__contains = search_word) | Q(body__contains = search_word),user_id=User.objects.get(user_id=user_id)).order_by('posted_date').reverse()[0:]
        else:
            context['data'] = Data.objects.filter(user_id=User.objects.get(user_id=user_id)).order_by('posted_date').reverse()[0:]

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
            return context
        else: # 不正アクセス
           template_name = 'error.html'


class EditView(LoginRequiredMixin,TemplateView):
    template_name = 'edit.html'
    # アクセスしてきたときにhtmlと入力フォームを返す
    def get_context_data(self, index, *args, **kwargs):
        user_id = self.request.user.user_id
        context = super().get_context_data(**kwargs)
        col = Data.objects.get(id=index)
        if col.user.user_id == user_id: # 修正するcolのuseridがgetのidと等しいとき
            initial = {'user':col.user,
                       'title':col.title,
                       'posted_date':col.posted_date,
                       'body': col.body,
                       'chat_type':col.chat_type,
                       'release':col.release}
            form = EditForm(initial=initial)
            context['data'] = col
            context['id'] = user_id
            context['form'] = form
            return context
        else: # 不正アクセス
           template_name = 'error.html'
    
    # editpageで修正ボタンが押されてPOST requestが飛んできたとき
    def post(self, request, index, *args, **kwargs):
        user_id = self.request.user.user_id
        form = EditForm(request.POST)
        if form.is_valid():
            title = form['title'].value
            body = form['body'].value
            Data.objects.update_or_create(id=index,
                                          defaults={
                                              'title':title,
                                              'body':body
                                            })

            return redirect("detail_page",index=index)
        else: # 不正削除
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
        context['release_chat_type'] = ChatType.objects.filter(~Q(id__in=chat_type_number_list),release=True)[0:5]
        return context

    
    # editpageで修正ボタンが押されてPOST requestが飛んできたとき
    def post(self, request, *args, **kwargs):
        user_id = self.request.user.user_id
        selected_values = request.POST.getlist('check[]')
        col = User.objects.get(user_id=user_id)
        col.chat_type = str(request.POST.getlist('check[]'))
        col.save()
        print(selected_values)
        print(type(selected_values))
        return redirect("top_page")
