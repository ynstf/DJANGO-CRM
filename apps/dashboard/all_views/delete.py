from django.shortcuts import get_object_or_404, redirect
from ..models import PhoneNumber, WhatsApp, Email, Landline, Address, Inquiry


def delete_number_view(request, id_number):
    phone = get_object_or_404(PhoneNumber, id=id_number)
    id = phone.customer.id
    phone.delete()
    return redirect('edit_customer', id=id)

def delete_whatsApp_view(request, id_number):
    whatsApp = get_object_or_404(WhatsApp, id=id_number)
    id = whatsApp.customer.id
    whatsApp.delete()
    return redirect('edit_customer', id=id)

def delete_email_view(request, id_mail):
    mail = get_object_or_404(Email, id=id_mail)
    id = mail.customer.id
    mail.delete()
    return redirect('edit_customer', id=id)

def delete_landline_view(request, id_number):
    landline = get_object_or_404(Landline, id=id_number)
    id = landline.customer.id
    landline.delete()
    return redirect('edit_customer', id=id)

def delete_address_view(request, id_address):
    address = get_object_or_404(Address, id=id_address)
    id = address.customer.id
    address.delete()
    return redirect('edit_customer', id=id)

def delete_inquiry_view(request, id_inq):
    inquiry = get_object_or_404(Inquiry, id=id_inq)
    id = inquiry.customer.id
    inquiry.delete()
    return redirect('edit_customer', id=id)

