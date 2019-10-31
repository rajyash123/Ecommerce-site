from django import forms
from django_countries.fields import CountryField

PAYMENT_CHOICES = (
    ('S', 'Stripes'),
    ('P', 'Paypal')
)

# creating the django form for checkout
class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'1234 Main St.'}))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Colony or apartment Name'}))
    country = CountryField(blank_label='(select country)').formfield(attrs={'class':'custom-select d-block w-100'})
    zip_code = forms.CharField()
    same_billing_address = forms.BooleanField(widget=forms.CheckboxInput())
    save_info = forms.BooleanField(widget=forms.CheckboxInput())
    payment_option = forms.ChoiceField(widget=forms.RadioSelect(), choices=PAYMENT_CHOICES)
    

class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control',
        'placeholder':'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))

class RefundForm(forms.Form):
    ref_code = forms.CharField()
    messages = forms.CharField(widget=forms.Textarea(attrs={'rows':4}))
    email = forms.EmailField()