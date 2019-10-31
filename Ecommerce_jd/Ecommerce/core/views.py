from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from .models import Item, OrderItem, Order, Address, Payment, Coupon, Refund
from .forms import CheckoutForm, CouponForm, RefundForm
from django.contrib import messages

import random
import string
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.

# creating a random reference code
def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

def item_list(request):
    context = {
        'items': Item.objects .all()
    }

    return render(request, 'item_list.html', context)

class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = 'home-page.html'

# shows the order summary of the product that we have ordered
class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):

        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, 'You do not have an object')
            return redirect('/')


class ItemDetailView(DetailView):
    model = Item
    template_name = 'product.html'

class CheckoutView(View):
    def get(self, *args, **kwargs):
        # trying to get the order
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            # form
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order
            }
            
            return render(self.request, 'checkout.html', context)
        except ObjectDoesNotExist:
            messages.info(this.request, 'error in getting the order')
            return redirect('checkout')

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered = False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # TODO: add functionality to these fields
                # same_billing_address = form.cleaned_data.get('same_billing_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = Address(
                    user=self.request.user,
                    street_address = street_address,
                    apartment_address = apartment_address,
                    country = country,
                    zip = zip,
                    address_type = 'B'
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                
                if payment_option == "S":
                    return redirect('payment', payment_option='stripe')
                elif payment_option == "P":
                    return redirect('payment', payment_option='paypal')
                else:
                    messages.warning(self.request, 'Failed checkout')
                    return redirect('checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, 'You do not have an active Order')
            return redirect('order-summary')


class PaymentView(View):
    def get(self, *args, **kwargs):
        return render(self.request, 'payment.html')

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)


        try:
            charge = stripe.Charge.create(
                amount=order.get_total()*100,        # cent
                currency='usd',
                source=token,
            )

            # create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # assigns the payment to the order

            order_items = order.items.all()
            order_items.update(ordered=False)
            for item in order_items:
                item.save()

            order.ordered = True
            order.payment = payment
            # TODO: assign the ref_code
            order.ref_code = create_ref_code()
            order.save()

            messages.success(self.request, "your order was successfull")
            return redirect('/')
            
        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            
        except stripe.error.RateLimitError as e:
            messages.warning(self.request, "Rate limit error")

        except stripe.error.InvalidRequestError as e:
            messages.warning(self.request, "Invalid parameters")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
             # Network communication with Stripe failed
            messages.warning(self.request, "Network error")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(self.request, "Network error")
            return redirect("/")
        
        except stripe.error.StripeError as e:
             # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.warning(
                self.request, "Something went wrong. You were not charged. Please try again.")
            return redirect("/")

        except Exception as e:
             # send an email to ourselves
            messages.warning(
                self.request, "A serious error occurred. We have been notifed.")
            return redirect("/")      

# adding an item to the cart
@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, 'This item quantity was updated')
            return redirect('order-summary')
        else:
            messages.info(request, f'This item was added to your cart')
            order.items.add(order_item)
            return redirect('order-summary')
    # if the order doesn't exists
    else:
        ordered_date = timezone.now() 
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, 'This item was added to your cart.')
        return redirect('order-summary')

@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user,  ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        # check if the order is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            order.items.remove(order_item)
            messages.info(request, 'This item was removed from your cart')
        else:
            # add a message saying the user order does not created contain the order
            messages.info(request, 'This item was not in your cart')
            return redirect('order-summary')
    else:
        # add a message saying the user doesn't have an order
        messages.info(request, 'You do not have an active order')
        return redirect('order-summary')
    return redirect('order-summary')

# this is for removing the single item from the cart
@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.item.remove(order_item)
            messages.info(request, 'This item quantity was updated.')
            return redirect('order-summary')
        else:
            messages.info(request, "This item was not in your cart.")
            return redirect("order-summary")
    else:
        messages.info(request, "You do not have an active order.")
        return redirect('order-summary')

def get_coupon(code):
    try:
        coupon = Coupon.objects.get(code=code)

    except ObjectDoesNotExist:
        messages.info(request, 'You do not have an active order')
        return redirect('checkout')


def add_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user=request.user, ordered=False)
                coupon = get_coupon(request, code)
                order.coupon = get_coupon(request, code)
                order.save()
                messages.info(request, 'coupon added')
                return redirect('checkout')

            except ObjectDoesNotExist:
                messages.info(request, 'You do not have an active order')
                return redirect('checkout')
    # TODO: raise error

    return None

class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "successfull added a coupon")
                return redirect('checkout')
            except:
                messages.info(self.request, "you do not have a active order")
                return redirect("checkout")

class RequestRefundView(View):

    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form':form
        }
        return render(self.request, 'request_refund.html', context)


    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data('ref_code')
            message = form.cleaned_data('message')
            email = form.cleaned_data('email')

            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, 'your request was received')
                return redirect('request-refund')
            except ObjectDoesNotExist:
                messages.info(self.request, 'This order does not exist')
                return redirect('request-refund')