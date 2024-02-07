from django.contrib import admin
from .models import Service, Emirate, Source, Language, Nationality, Customer, PhoneNumber, WhatsApp, Landline, Email, Address, Inquiry, Booking

# Register your models here.

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Emirate)
class EmirateAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Nationality)
class NationalityAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'gender', 'nationality', 'register', 'language', 'source', 'trn')

@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('customer', 'number')

@admin.register(WhatsApp)
class WhatsAppAdmin(admin.ModelAdmin):
    list_display = ('customer', 'number')

@admin.register(Landline)
class LandlineAdmin(admin.ModelAdmin):
    list_display = ('customer', 'number')

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('customer', 'email')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('customer', 'address_name', 'type', 'emirate', 'description_location', 'location')

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('customer', 'address', 'date_inq', 'inq_num', 'description')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('inquiry', 'booking_num', 'booking_date', 'description')
