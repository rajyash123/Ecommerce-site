from django.urls import path
from .views import blogHome
urlpatterns = [
    path('', blogHome, name='blog-home')
]