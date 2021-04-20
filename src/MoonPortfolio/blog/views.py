from django.http.response import Http404
from django.shortcuts import render, redirect
from .models import Post

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import PostForm

@login_required(login_url='login')
def blog_index(request):
    post = Post.objects.all()
    context = {'posts': post}
    return render(request, 'blog/blog_index.html', context)

@login_required(login_url='login')
def post(request, post_name):
    try:
        post = Post.objects.get(title=post_name)
        context = {'post': post}
    except:
        context = {'message': 'Article does not exists'}

    return render(request, 'blog/post.html', context)

@login_required(login_url='login')
def add_post(request):

    if not request.user.is_authenticated:
        raise Http404


    form = PostForm(request.POST, request.FILES)
    if form.is_valid():
        instance = form.save()
        instance.author = request.user
        instance.save()
        messages.success(request, "Successfully Created")

        return redirect('blog')

    context = {'form' : form}

    return render(request, 'blog/add_post.html', context)

@login_required(login_url='login')
def edit_post(request, pk):

    if not request.user.is_authenticated:
        raise Http404

    post = Post.objects.get(id=pk)
    form = PostForm(instance=post)

    if form.is_valid():
        instance = form.save()
        instance.save()
        messages.success(request, "Successfully Created")

        return redirect('blog')

    context = {'form' : form}

    return render(request, 'blog/add_post.html', context)

@login_required(login_url='login')
def delete_post(request, pk):

    post = Post.objects.get(id=pk)

    if request.method == 'POST':
        post.delete()
        redirect('blog')
    
    context = {'post': post}
    return render(request, 'blog/delete.html', context)