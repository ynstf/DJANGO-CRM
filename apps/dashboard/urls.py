from django.urls import path
from .views import dashboard,add_customer,customer_list,customer_info,edit_customer
from .views import delete_number, delete_whatsApp, delete_landline, delete_email, delete_address,delete_inquiry,delete_number
from .views import get_languages, get_nationalities,get_sources
from .views import inquiries_list,inquiry_info,make_quotation,edit_quotation

urlpatterns = [
    path("dashboard/",dashboard,name="dashboard",),
    path('add_customers/', add_customer, name='add_customer'),
    path('customer_list/', customer_list, name='customer_list'),
    path('customer/<int:id>', customer_info, name='customer_info'),
    path('customer/<int:id>/edit/', edit_customer, name='edit_customer'),

    path('delete_number/<int:id_number>', delete_number, name='delete_number'),
    path('delete_whatsApp/<int:id_number>', delete_whatsApp, name='delete_whatsApp'),
    path('delete_landline/<int:id_number>', delete_landline, name='delete_landline'),
    path('delete_email/<int:id_mail>', delete_email, name='delete_email'),
    path('delete_address/<int:id_address>', delete_address, name='delete_address'),
    path('delete_inquiry/<int:id_inq>', delete_inquiry, name='delete_inquiry'),

    path('get_languages', get_languages, name='get_languages'),
    path('get_nationalities', get_nationalities, name='get_nationalities'),
    path('get_sources', get_sources, name='get_sources'),


    
    path('inquiries_list', inquiries_list, name='inquiries_list'),
    path('inquiry/<int:id>', inquiry_info, name='inquiry_info'),
    path('make_quotation/<int:id>', make_quotation, name='make_quotation'),
    path('edit_quotation/<int:id>', edit_quotation, name='edit_quotation'),


    

]
