from django.shortcuts import render
from django.http import HttpResponse
from .models import BlogPost
# Create your views here.

def home(request, id):

    return render(request, 'blog/home.html')

def blogpost(request, id):
    post = BlogPost.objects.filter(post_id=id)[0]
    print(post)
    context = {
        'post':post
    }
    return render(request, 'blog/blogpost.html', context)

