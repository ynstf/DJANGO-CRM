from django.urls import path
from .views import dashboard,add_customer,customer_list,customer_info,edit_customer
from .views import delete_number, delete_whatsApp, delete_landline, delete_email, delete_address,delete_inquiry,delete_number
from .views import get_languages, get_status, get_nationalities,get_sources,get_services, make_inq_connecting, make_inq_sendQ, make_inq_pending
from .views import notifications, get_notifications,inquiries_list,inquiry_info,make_quotation,edit_quotation,generate_pdf
from .views import add_employee,employee_list,delete_user,employee_info,edit_employee,add_service,services_list
from .views import make_booking, make_inq_underproccess, make_inq_new,generate_invoice,get_notify_state,make_employee_notified

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
    path('get_services', get_services, name='get_services'),
    path('get_status', get_status, name='get_status'),


    
    path('notifications', notifications, name='notifications'),
    path('get_notifications/', get_notifications, name='get_notifications'),
    path('get_notify_state/', get_notify_state, name='get_notify_state'),
    path('make_employee_notified/', make_employee_notified, name='make_employee_notified'),
    path('inquiries_list', inquiries_list, name='inquiries_list'),
    path('inquiry/<int:id>', inquiry_info, name='inquiry_info'),
    path('make_quotation/<int:id>', make_quotation, name='make_quotation'),
    path('edit_quotation/<int:id>', edit_quotation, name='edit_quotation'),
    path('generate_pdf/<int:id>/', generate_pdf, name='generate_pdf'),


    path('generate_invoice/<int:id>/', generate_invoice, name='generate_invoice'),

    path('make_booking/<int:id>', make_booking, name='make_booking'),
    path('make_inq_underproccess/<int:inq_id>', make_inq_underproccess, name='make_inq_underproccess'),
    path('make_inq_new/<int:inq_id>', make_inq_new, name='make_inq_new'),
    path('make_inq_connecting/<int:inq_id>', make_inq_connecting, name='make_inq_connecting'),
    path('make_inq_sendQ/<int:inq_id>', make_inq_sendQ, name='make_inq_sendQ'),
    path('make_inq_pending/<int:inq_id>', make_inq_pending, name='make_inq_pending'),
    

    path('add_employee/', add_employee, name='add_employee'),
    path('employee_list/', employee_list, name='employee_list'),
    path('delete_user/<int:id_user>', delete_user, name='delete_user'),
    path('employee_info/<int:id>', employee_info, name='employee_info'),
    path('employee_info/<int:id>/edit', edit_employee, name='edit_employee'),

    path('add_service/', add_service, name='add_service'),
    path('services_list/', services_list, name='services_list'),



    

]
