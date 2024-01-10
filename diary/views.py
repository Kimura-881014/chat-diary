from django.shortcuts import render, redirect
from django.urls import reverse
from urllib.parse import urlencode

# Create your views here.
from django.views.generic import TemplateView
from .models import Data
from .forms import EditForm

from django.db.models import Q


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self,user_id, **kwargs):
        context = super().get_context_data(**kwargs)
        # user_id = (self.request.GET.get('id'))
        if 'page' in self.request.GET:
            page = int(self.request.GET.get('page'))
        else:
            pass

        if 'search' in self.request.GET:
            search_word = self.request.GET.get('search')
            context['data'] = Data.objects.filter(Q(title__contains = search_word) | Q(body__contains = search_word),user_id=user_id)[0:]
        else:
            context['data'] = Data.objects.filter(user_id=user_id)[0:]

        context['id'] = user_id

        return context
    


class DetailView(TemplateView):
    template_name = 'detail.html'

    def get_context_data(self, user_id, index, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        # user_id = (self.request.GET.get('id'))
        # index = int(self.request.GET.get('index'))
        col = Data.objects.get(id=index)
        if col.user_id == user_id: # 見ようとしているcolのuseridがgetのidと等しいとき
            context['data'] = col
            context['id'] = user_id
            context['row'] = len(col.body)/40 + 3
            return context
        else: # 不正アクセス
           template_name = 'error.html'


class EditView(TemplateView):
    template_name = 'edit.html'
    # アクセスしてきたときにhtmlと入力フォームを返す
    def get_context_data(self, user_id, index, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        col = Data.objects.get(id=index)
        if col.user_id == user_id: # 修正するcolのuseridがgetのidと等しいとき
            initial = {'user_id':user_id,
                       'title':col.title,
                       'posted_date':col.posted_date,
                       'body': col.body,}
            form = EditForm(initial=initial)
            context['data'] = col
            context['id'] = user_id
            context['form'] = form
            return context
        else: # 不正アクセス
           template_name = 'error.html'
    
    # editpageで修正ボタンが押されてPOST requestが飛んできたとき
    def post(self, request, user_id, index, *args, **kwargs):
        form = EditForm(request.POST)
        if form.is_valid():
            title = form['title'].value
            body = form['body'].value
            Data.objects.update_or_create(id=index,
                                          defaults={
                                              'title':title,
                                              'body':body
                                            })

            return redirect("detail_page", user_id=user_id,index=index)
    
class MyDeleteView(TemplateView):
    def get(self, request, user_id, index, *args, **kwargs):
        # user_id = (self.request.GET.get('id'))
        # index = int(self.request.GET.get('index'))
        col = Data.objects.get(id=index)
        if col.user_id == user_id: # 消そうとしているcolのuseridがgetのidと等しいとき
            col.delete()
            url = reverse('top_page', kwargs={'user_id':user_id})
            parameters = urlencode({'page':1})
            # parameters = urlencode({'id':user_id,'page':1})
            return redirect(f'{url}?{parameters}')
        else: # 不正削除
           return render(request, 'error.html')