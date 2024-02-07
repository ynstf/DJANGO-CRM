# models.py
from django.db import models
from apps.authentication.models import Employee


class Service(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
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
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, blank=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=6, choices=[('male', 'Male'), ('female', 'Female')])
    nationality = models.ForeignKey(Nationality, on_delete=models.CASCADE)  # Link to the Nationality model
    register = models.DateTimeField(auto_now_add=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)  # Link to the Language model
    source = models.ForeignKey(Source, on_delete=models.CASCADE)  # Link to the Source model
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
    number = models.CharField(max_length=20)

    def __str__(self):
        return self.number

class Landline(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    number = models.CharField(max_length=20)

    def __str__(self):
        return self.number

class Email(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    email = models.EmailField()

    def __str__(self):
        return self.email

class Address(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    address_name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=[('house', 'House'), ('company', 'Company')])
    emirate = models.ForeignKey(Emirate, on_delete=models.CASCADE)  # Link to the Emirate model
    description_location = models.TextField()
    location = models.CharField(max_length=100)
    # Add other fields as needed
    def __str__(self):
        return f'{self.customer} - {self.address_name}'

class Inquiry(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, blank=True, null=True)
    date_inq = models.DateField()
    time_inq = models.TimeField()
    inq_num = models.CharField(max_length=50)
    services = models.ManyToManyField(Service)
    description = models.TextField()
    # Add other fields as needed
    def __str__(self):
        return f'{self.customer} - {self.address} - {self.services}'

class Booking(models.Model):
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE)
    booking_num = models.CharField(max_length=50)
    booking_date = models.DateField()
    description = models.TextField()
    # Add other fields as needed

    def __str__(self):
        return f'{self.inquiry}'
    
class tab(models.Model):
    description = models.TextField()
    # Add other fields as needed
    def __str__(self):
        return f'{self.description}'
