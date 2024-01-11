from .views import IndexView, index
from django.urls import path

urlpatterns = [
    # path('/', IndexView.as_view(),name="top_page"),
    path('/', index(),name="call_back"),
]



