from django.shortcuts import render

def blog_index(request):
    return render(request, 'blog/blog_index.html')

def article(request, name):
    return render(request, 'blog/article.html')
