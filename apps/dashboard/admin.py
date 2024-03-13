from django.contrib import admin
from .models import Service, Emirate, Source, Language, Nationality, PhoneNumber, WhatsApp, Landline, Email
from .models import Customer, Address, Inquiry, Quotation, Booking, InquiryNotify
from .models import Status,InquiryStatus
from .models import Service


# Register your models here.

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name','columns')

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
    list_display = ('first_name', 'last_name', 'gender', 'nationality', 'register', 'language', 'trn')

@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('customer', 'number')

@admin.register(WhatsApp)
class WhatsAppAdmin(admin.ModelAdmin):
    list_display = ('customer', 'whatsapp')

@admin.register(Landline)
class LandlineAdmin(admin.ModelAdmin):
    list_display = ('customer', 'landline')

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('customer', 'email')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('customer', 'address_name', 'type', 'emirate', 'description_location', 'location')

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('customer', 'address', 'date_inq', 'source', 'description')


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(InquiryStatus)
class InquiryStatusAdmin(admin.ModelAdmin):
    list_display = ('inquiry', 'status')

@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ('customer', 'inquiry', 'quotation_service', 'quotation_date', 'total')

@admin.register(InquiryNotify)
class InquiryNotifyAdmin(admin.ModelAdmin):
    list_display = ('employee', 'inquiry', 'service','action')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('customer', 'inquiry', 'booking_service', 'booking_date', 'details', 'booking_number')
