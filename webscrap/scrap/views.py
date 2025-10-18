from django.shortcuts import render
from rest_framework import generics
from .models import Article
from .serializers import ArticleSerializer
from urllib.parse import urlparse

# Create your views here.
class ArticleViewList(generics.ListAPIView):
    """
    Endpoint który zwróci listę wszystkich artykułów
    """
    serializer_class = ArticleSerializer
    def get_queryset(self):
        queryset = Article.objects.all().order_by('-published_at')
        source_domain = self.request.query_params.get('source', None)
        if source_domain:
            queryset = [a for a in queryset if urlparse(a.url).netloc == source_domain]
        return queryset

class ArticleDetailAPI(generics.RetrieveAPIView):
    """
    Endpoint który zwróci szczegóły artykułu
    """
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

