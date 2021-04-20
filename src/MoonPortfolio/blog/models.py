from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Post(models.Model):

    title = models.CharField(max_length=400)
    headline = models.CharField(max_length=400, null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    date = models.DateField(auto_now=True)
    body = models.TextField()
    image = models.ImageField(null=True, blank=True, upload_to="static/img", default="static/img/placeholder.png")

    def __str__(self):
        return self.title