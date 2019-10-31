from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Product, Contact, Order, OrderUpdate
from math import ceil
import json
# Create your views here.

def online_home(request):
    products = Product.objects.all()
    n = len(products)
    no_slides = n//4 * ceil((n/4) - (n//4))
    context = {
        'products': products
    }
    return render(request, 'online/home.html', context)

def about(request):
    return render(request, 'online/about.html')

def contact(request):
    thank = False
    if request.method == 'POST':
        name = request.POST.get('name','')
        email = request.POST.get('email','')
        phone = request.POST.get('phone','')
        description = request.POST.get('description', '')
        contact = Contact(name=name, email=email, phone=phone, description=description)
        contact.save()
        thank = True
        return redirect('contact')
    return render(request, 'online/contact.html', {'thank':thank})

def tracker(request):
    if request.method == 'POST':
        order_id = request.POST.get('orderId','')
        email = request.POST.get('email','')
        try:
            order = Order.objects.filter(order_id=order_id, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=order_id)
                updates = []
                for item in update:
                    updates.append({'item':item.update_desc, 'time':item.timestamp})
                    response = json.dumps([updates, order[0].item_json], default=str)
                    return HttpResponse(response)
            else:
                return HttpResponse('error')
        except Exception as e:
            return HttpResponse(f'error {e}')

    return render(request, 'online/tracker.html')

def search(request):
    return HttpResponse('we are at search')

def product_view(request, id):
    # fetch the product using the id
    product = Product.objects.filter(id=id)
    print(product)
    return render(request, 'online/products-view.html', {'product':product[0]})

def checkout(request):
    if request.method == 'POST':
        item_json = request.POST.get('itemJson', '')
        name = request.POST.get('name','')
        email = request.POST.get('email','')
        address = request.POST.get('address', '') + '' + request.POST.get('address2', '')
        state = request.POST.get('state', '')
        city = request.POST.get('city', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone','')
        order = Order(item_json=item_json, name=name, email=email, address=address, city=city, state=state, phone=phone, zip_code=zip_code)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc='the order has been placed')
        update.save()
        thank = True
        id = order.order_id
        context = {
            'thank':thank,
            'id': id
        }
        return render(request, 'online/checkout.html', context)
    return render(request, 'online/checkout.html')
