# forms.py

from django import forms
from .models import Customer, Address, Inquiry, Booking
from .models import PhoneNumber, WhatsApp, Landline, Email, Address, Emirate

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'

    # Explicitly include related fields
    landlines = forms.CharField(required=False)
    phone_numbers = forms.CharField(required=False)
    whats_apps = forms.CharField(required=False)
    emails = forms.CharField(required=False)
    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        # Exclude the ForeignKey fields from the form
        self.fields['employee'].widget = forms.HiddenInput()
class CustomerFormEdit(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CustomerFormEdit, self).__init__(*args, **kwargs)
        # Exclude the ForeignKey fields from the form
        self.fields['employee'].widget = forms.HiddenInput()


class AddressForm(forms.ModelForm):
    emirate = forms.ModelChoiceField(queryset=Emirate.objects.all(), required=False)

    class Meta:
        model = Address
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        # Exclude the ForeignKey fields from the form
        self.fields['customer'].widget = forms.HiddenInput()

class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = '__all__'


    def __init__(self, *args, **kwargs):
        super(InquiryForm, self).__init__(*args, **kwargs)
        # Exclude the ForeignKey fields from the form
        self.fields['customer'].widget = forms.HiddenInput()
        self.fields['address'].widget = forms.HiddenInput()

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = '__all__'

class PhoneNumberForm(forms.ModelForm):
    class Meta:
        model = PhoneNumber
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(PhoneNumberForm, self).__init__(*args, **kwargs)
        # Exclude the ForeignKey fields from the form
        self.fields['customer'].widget = forms.HiddenInput()

class WhatsAppForm(forms.ModelForm):
    class Meta:
        model = WhatsApp
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(WhatsAppForm, self).__init__(*args, **kwargs)
        # Exclude the ForeignKey fields from the form
        self.fields['customer'].widget = forms.HiddenInput()

class LandlineForm(forms.ModelForm):
    class Meta:
        model = Landline
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(LandlineForm, self).__init__(*args, **kwargs)
        # Exclude the ForeignKey fields from the form
        self.fields['customer'].widget = forms.HiddenInput()

class EmailForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(EmailForm, self).__init__(*args, **kwargs)
        # Exclude the ForeignKey fields from the form
        self.fields['customer'].widget = forms.HiddenInput()


