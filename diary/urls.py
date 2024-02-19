from .views import LoginView, IndexView, DetailView, MyDeleteView, EditView, ChatTypeView
from django.urls import path

urlpatterns = [
    path('login/',LoginView.as_view(),name="login_page"),
    path('', IndexView.as_view(),name="top_page"),
    path('chat-type/',ChatTypeView.as_view(),name="chat_type"),
    path('<int:index>/',DetailView.as_view(), name="detail_page"),
    path('<int:index>/edit/',EditView.as_view(), name="edit"),
    path('<int:index>/delete/',MyDeleteView.as_view(), name="delete"),
]
# urlpatterns = [
#     path('<slug:user_id>/', IndexView.as_view(),name="top_page"),
#     path('<slug:user_id>/<int:index>/',DetailView.as_view(), name="detail_page"),
#     path('<slug:user_id>/<int:index>/edit/',EditView.as_view(), name="edit"),
#     path('<slug:user_id>/<int:index>/delete/',MyDeleteView.as_view(), name="delete"),
# ]