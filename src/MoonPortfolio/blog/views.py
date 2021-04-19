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
    form = PostForm()

    if (request.method == "POST"):
        form = PostForm(request.POST)
        if form.is_valid():

            post = form.save()
            post.author = request.user.id
            post.save()
 
            title = form.cleaned_context.get('title')
            messages.success(request, 'Post \"'+title+ '\" was succesfully created !')

            return redirect('blog')

        else:
            title = form.cleaned_context.get('title')
            messages.error(request, 'Post \"'+title+ '\" was not created')

    context = {'form' : form}

    return render(request, 'blog/add_post.html', context)

@login_required(login_url='login')
def edit_post(request):

    return render(request, 'blog/edit_post.html')