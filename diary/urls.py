from .views import IndexView, DetailView, MyDeleteView, EditView
from django.urls import path

urlpatterns = [
    path('<slug:user_id>/', IndexView.as_view(),name="top_page"),
    path('<slug:user_id>/<int:index>/',DetailView.as_view(), name="detail_page"),
    path('<slug:user_id>/<int:index>/edit/',EditView.as_view(), name="edit"),
    path('<slug:user_id>/<int:index>/delete/',MyDeleteView.as_view(), name="delete"),
]