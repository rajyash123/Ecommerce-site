from django.urls import path, include
from . import views

# active urls of the site
urlpatterns = [
    path('', views.online_home, name='home'),
    path('about/', views.about, name='AboutUs'),
    path('contact/', views.contact, name='contact'),
    path('tracker/', views.tracker, name='TrackingStatus'),
    path('search/', views.search, name='Search'),
    path('products/<int:id>/', views.product_view, name='online_product'),
    path('checkout/', views.checkout, name='Checkout'),
]

