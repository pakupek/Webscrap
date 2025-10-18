from datetime import datetime
from django.db import models


class Article(models.Model):
    """Artykuł"""
    title = models.CharField(max_length=500)
    url = models.URLField(unique=True)
    content_html = models.TextField() 
    content_text = models.TextField()                 
    published_at = models.CharField(max_length=19)
    scraped_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return self.title
    