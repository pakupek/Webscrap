from django.urls import path
from .views import ArticleViewList, ArticleDetailAPI

urlpatterns = [
    path('articles/<int:pk>', ArticleDetailAPI.as_view(), name='article-detail'),
    path('articles/', ArticleViewList.as_view(), name='article-list')
]