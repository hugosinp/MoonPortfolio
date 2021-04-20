from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'headline', 'image', 'body']
        labels = {
            "title" : "Post Title",
            "image" : "Thumbnail",
            "body" : "Post body"
        }