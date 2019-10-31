from django.urls import path
from .views import (item_list, CheckoutView, ItemDetailView, HomeView, add_to_cart, remove_from_cart, OrderSummaryView, 
                    remove_single_item_from_cart, PaymentView, add_coupon, RequestRefundView)

urlpatterns = [
    path('', HomeView.as_view(), name='item_list'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add_to_cart'),
    path('add-coupon/', add_coupon, name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove_from_cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart, name='remove_single_item_from_cart'),
    path('payment/<payment_option>', PaymentView.as_view(), name='payment'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund')
]
