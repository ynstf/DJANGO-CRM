from django.contrib import admin
from apps.dashboard.models import Invoice
from .models import Service, Emirate, Source, Language, Nationality, PhoneNumber, WhatsApp, Landline, Email
from .models import Customer, Address, Inquiry, Quotation, Booking, InquiryNotify
from .models import Status,InquiryStatus, IsEmployeeNotified
from .models import Service, InquiryReminder,SuperProvider
from .models import InvoiceForm, QuotationForm, Advence, Complain, Message, MessageNotify, IsEmployeeReadMessage, GroupMessenger, MessageGroup


# Register your models here.

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name','number','columns','description','reminder_time')

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

@admin.register(GroupMessenger)
class GroupMessengerAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(MessageGroup)
class MessageGroupAdmin(admin.ModelAdmin):
    list_display = ('group',)

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

@admin.register(Complain)
class ComplainAdmin(admin.ModelAdmin):
    list_display = ( 'inquiry', 'detail', 'opened', 'closed')

@admin.register(SuperProvider)
class SuperProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'trn')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('inquiry', 'source', 'destination')


@admin.register(QuotationForm)
class QuotationFormAdmin(admin.ModelAdmin):
    list_display = ('title', 'image', 'email', 'phone')


@admin.register(InvoiceForm)
class InvoiceFormAdmin(admin.ModelAdmin):
    list_display = ('title', 'image', 'email', 'phone')


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(InquiryStatus)
class InquiryStatusAdmin(admin.ModelAdmin):
    list_display = ('inquiry', 'status')

@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ('customer', 'inquiry', 'quotation_service', 'quotation_date', 'data', 'total')

@admin.register(InquiryNotify)
class InquiryNotifyAdmin(admin.ModelAdmin):
    list_display = ('employee', 'inquiry', 'sp','action')

@admin.register(IsEmployeeNotified)
class IsEmployeeNotifiedAdmin(admin.ModelAdmin):
    list_display = ('employee','notified')


@admin.register(MessageNotify)
class MessageNotifyAdmin(admin.ModelAdmin):
    list_display = ('employee', 'source','inquiry', 'service','sp')

@admin.register(IsEmployeeReadMessage)
class IsEmployeeReadMessageAdmin(admin.ModelAdmin):
    list_display = ('employee','notified','sp')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('customer', 'inquiry', 'booking_service', 'booking_date', 'details', 'booking_number')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('customer', 'inquiry', 'quotation_service', 'quotation_date', 'data', 'total')

@admin.register(InquiryReminder)
class InquiryReminderAdmin(admin.ModelAdmin):
    list_display = ('employee', 'inquiry', 'service', 'schedule')

@admin.register(Advence)
class AdvenceAdmin(admin.ModelAdmin):
    list_display = ('inquiry',)
