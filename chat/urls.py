from .views import IndexView, call_back
from django.urls import path

urlpatterns = [
    # path('', IndexView.as_view(),name="top_page"),
    path('', call_back,name="call_back"),
]



