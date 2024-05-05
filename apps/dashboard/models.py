# models.py
from django.db import models
from apps.authentication.models import Employee
from .models_com import Service
from django.db import models
from .models_com import SuperProvider



class Emirate(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class Source(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Language(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Nationality(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Customer(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=6, choices=[('male', 'Male'), ('female', 'Female')], blank=True, null=True)
    nationality = models.ForeignKey(Nationality, on_delete=models.SET_NULL, blank=True, null=True)  # Link to the Nationality model
    register = models.DateTimeField(auto_now_add=True)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, blank=True, null=True)  # Link to the Language model
    trn = models.CharField(max_length=50, blank=True, null=True)
    
    # Add other fields as needed
    def __str__(self):
        return f'{self.first_name} - {self.last_name}'

class PhoneNumber(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    number = models.CharField(max_length=20)

    def __str__(self):
        return self.number

class WhatsApp(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    whatsapp = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.whatsapp

class Landline(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    landline = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.landline

class Email(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.email

class Address(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    address_name = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=10, choices=[('house', 'House'), ('company', 'Company')], blank=True, null=True)
    emirate = models.ForeignKey(Emirate, on_delete=models.SET_NULL, blank=True, null=True)  # Link to the Emirate model
    description_location = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    location_url = models.URLField(blank=True, null=True)
    # Add other fields as needed
    def __str__(self):
        return f'{self.customer} - {self.address_name}'

class Inquiry(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, blank=True, null=True)
    date_inq = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    services = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True)
    sp = models.ForeignKey(SuperProvider, on_delete=models.SET_NULL, blank=True, null=True)
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, blank=True, null=True)  # Link to the Source model
    description = models.TextField(blank=True, null=True)
    cloudinary_urls = models.TextField(blank=True, null=True)
    handler = models.ManyToManyField(Employee, blank=True, null=True)
    owner = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True, related_name='owner')
    # Add other fields as needed
    def __str__(self):
        return f'{self.customer} - {self.address}'

class Message(models.Model):
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, blank=True, null=True)
    source = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True, related_name='sent_messages')
    destination = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True, related_name='recive_messages')
    content = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    
    def __str__(self):
        return f'{self.inquiry} source:{self.source} destination:{self.destination} '

class GroupMessenger(models.Model):
    name = models.CharField(max_length=80, blank=True, null=True)
    members = models.ManyToManyField(Employee, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)


    def __str__(self):
        return self.name

class MessageGroup(models.Model):
    group = models.ForeignKey(GroupMessenger, on_delete=models.CASCADE, blank=True, null=True)
    source = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f'{self.group} source:{self.source}'

class MessageNotify(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, blank=True, null=True, related_name='me')
    source = models.ForeignKey(Employee, on_delete=models.CASCADE, blank=True, null=True, related_name='of')
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, blank=True, null=True)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True)
    sp = models.ForeignKey(SuperProvider, on_delete=models.SET_NULL, blank=True, null=True)
    from_group = models.BooleanField(default=False)
    group = models.ForeignKey(GroupMessenger, on_delete=models.CASCADE, blank=True, null=True)


    def __str__(self):
        return f'message for {self.sp} {self.inquiry} inquiry'

class IsEmployeeReadMessage(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, blank=True, null=True)
    notified = models.BooleanField(default=False)
    sp = models.ForeignKey(SuperProvider, on_delete=models.SET_NULL, blank=True, null=True)
    # Add other fields as needed

    def __str__(self):
        return f'employee :{self.employee}'




class Complain(models.Model):
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE)
    opened = models.DateField(blank=True, null=True)
    detail = models.TextField(blank=True, null=True)
    closed = models.DateField(blank=True, null=True)
    fixe_detail = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f'{self.inquiry}'# : {self.detail[30]}'

class Status(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name

class InquiryStatus(models.Model):
    #employee = models.ForeignKey(Employee, on_delete=models.CASCADE, blank=True, null=True)
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    canceling_causes = models.CharField(max_length=200, blank=True, null=True)
    update = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return f'{self.inquiry} is {self.status}'

class EmployeeAction(models.Model):
    from_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True)
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    update = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return f'{self.inquiry} is {self.status}'

class Quotation(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    inquiry = models.ForeignKey(Inquiry, on_delete=models.SET_NULL, blank=True, null=True)
    quotation_service = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True)
    quotation_sp = models.ForeignKey(SuperProvider, on_delete=models.SET_NULL, blank=True, null=True)
    invoice_counter = models.CharField(max_length=50, blank=True, null=True)
    quotation_date = models.DateField(blank=True, null=True)
    data = models.TextField(blank=True, null=True)
    total = models.CharField(max_length=50, blank=True, null=True)
    # Add other fields as needed
    def __str__(self):
        return f'{self.customer} - {self.inquiry}'

class QuotationForm(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True)
    image = models.TextField( blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)

    # Add other fields as needed
    def __str__(self):
        return self.title

class InvoiceForm(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True)
    image = models.TextField( blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)

    # Add other fields as needed
    def __str__(self):
        return self.title

class InquiryNotify(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True)
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, blank=True, null=True)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True)
    sp = models.ForeignKey(SuperProvider, on_delete=models.SET_NULL, blank=True, null=True)
    action = models.CharField(max_length=50, choices=[('new', 'new'),
                                                    ('connecting', 'connecting'),
                                                    ('cancel', 'cancel'),
                                                    ('send quotation', 'send quotation'),
                                                    ('pending', 'pending'),
                                                    ('underpreccess', 'underpreccess'),
                                                    ('updated', 'updated'),
                                                    ('reminder', 'reminder'),
                                                    ('complain', 'complain'),
                                                    ('done', 'done'),
                                                    ], blank=True, null=True)
    # Add other fields as needed

    def __str__(self):
        return f'employee :{self.employee} with {self.inquiry} inquiry'

class IsEmployeeNotified(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, blank=True, null=True)
    notified = models.BooleanField(default=False)

    # Add other fields as needed

    def __str__(self):
        return f'employee :{self.employee}'

class InquiryReminder(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True)
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, blank=True, null=True)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True)
    schedule = models.DateField(blank=True, null=True)

    # Add other fields as needed

    def __str__(self):
        return f'employee :{self.employee} with {self.inquiry} inquiry and scheduled in {self.schedule}'

class Booking(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE)
    booking_service = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True)
    booking_date = models.DateField(blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    booking_number = models.CharField(max_length=50, blank=True, null=True)
    ref_number = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f'booking for {self.inquiry}'

class Invoice(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    inquiry = models.ForeignKey(Inquiry, on_delete=models.SET_NULL, blank=True, null=True)
    quotation_service = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True)
    quotation_date = models.DateField(blank=True, null=True)
    data = models.TextField(blank=True, null=True)
    total = models.CharField(max_length=50, blank=True, null=True)
    # Add other fields as needed
    def __str__(self):
        return f'{self.customer} - {self.inquiry}'

class Advence(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=80, blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return f'advence {self.inquiry}'