from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='blog-home'),
    path('blogpost/<int:id>/', views.blogpost, name='blogpost')
]