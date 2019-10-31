from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django_countries.fields import CountryField

CATEGORY_CHOICES = (
    ('S','Shirt'),
    ('SW','Sport Wear'),
    ('OW','Out Wear')
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping')
)

# list of item that we can purchase
class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=2)
    description = models.TextField()
    image = models.ImageField()
    slug = models.SlugField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("product", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse('add_to_cart', kwargs={
            'slug':self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse('remove_from_cart', kwargs={
            'slug': self.slug 
        })

# link between the order and the item
class OrderItem(models.Model):
    # class that link the order and item class
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    # return the information about the order
    def __str__(self):
        return f'{self.quantity} of {self.item.title}'
    
    # return the total price of the product
    def get_total_item_price(self):
        return self.quantity * self.item.price

    
    def get_total_discount_price(self):
        return self.quantity * self.item.discount_price

    # return the difference between the total and the discount amount
    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_price()
    
    # return the price -> the total price of the all the product
    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_price()
        return self.get_total_item_price()
    

# we store the item in this order cart as shopping cart
class Order(models.Model):
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey('Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    shipping_address = models.ForeignKey('Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)               # imported to moniter
    refund_granted = models.BooleanField(default=False)

    '''
    1. Item added to cart
    2. Adding a billing address
    (failed order)
    3. Payment
    (preproccessing processing, packaging etc.)
    4. being delivered
    5. Received
    6. Refunds
    '''

    def __str__(self):
        return self.user.username

    # total price of all product
    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total

# billing address of the form
class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

def __str__(self):
    return self.user.username


# class for keeping the track of the payment
class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class Coupon(models.Model):
    code = models.CharField(max_length=15)

    def __str__(self):
        return self.code

class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()
    
    def __str__(self):
        return f"{self.pk}"