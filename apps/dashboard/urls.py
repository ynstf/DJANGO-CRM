from django.urls import path
from .views import dashboard,get_messages,make_employee_readmessage,get_message_state,messages_list

# importation for documents
from .views import (generate_pdf,generate_invoice,
                    edit_invoice_doc, edit_quotation_doc)

# importation for inquiries
from .views import (inquiries_list,inquiry_info,
                    make_quotation,edit_quotation,
                    edit_booking, add_advence,
                    make_booking,make_complain,messages)

## importation for admin
# importation for employers
from .views import (add_employee,employee_list,delete_user,
                    employee_info,edit_employee)
# importation for Services and SPs
from .views import (add_service,services_list,add_sp,sp_list)
# importation for statisics
from .views import (statistics)

# importation for notifications
from .views import (notifications, get_notifications,
                    make_employee_notified)

# importation for customer
from .views import (merge_customer,add_customer,customer_list,
                    customer_info,edit_customer)

# importation for deleting
from .views import (delete_number, delete_whatsApp,
                    delete_landline,delete_email,delete_address,
                    delete_inquiry,delete_number)

# importation for get informations
from .views import (get_languages, get_status, get_nationalities,
                    get_sources, get_services, get_notify_state,
                    get_services_by_sp)

# importation for make inquiry state change
from .views import (make_inq_connecting, make_inq_sendQ,
                    make_inq_pending, make_inq_cancel,
                    make_inq_underproccess, make_inq_new,
                    make_inq_complain, make_inq_done)


urlpatterns = [

    path("dashboard/",dashboard,name="dashboard"),

    # admin
    path('add_employee/', add_employee, name='add_employee'),
    path('add_sp/', add_sp, name='add_sp'),
    path('employee_list/', employee_list, name='employee_list'),
    path('sp_list/', sp_list, name='sp_list'),
    path('delete_user/<int:id_user>', delete_user, name='delete_user'),
    path('employee_info/<int:id>', employee_info, name='employee_info'),
    path('employee_info/<int:id>/edit', edit_employee, name='edit_employee'),
    path('add_service/', add_service, name='add_service'),
    path('services_list/', services_list, name='services_list'),
    path('statistics/', statistics, name='statistics'),

    # documents
    path('edit_invoice_doc/', edit_invoice_doc, name='edit_invoice_doc'),
    path('edit_quotation_doc/', edit_quotation_doc, name='edit_quotation_doc'),
    path('generate_pdf/<int:id>', generate_pdf, name='generate_pdf'),
    path('generate_invoice/<int:id>/', generate_invoice, name='generate_invoice'),

    # customer
    path('add_customers/', add_customer, name='add_customer'),
    path('customer_list/', customer_list, name='customer_list'),
    path('customer/<int:id>', customer_info, name='customer_info'),
    path('merge_customer/<int:id>', merge_customer, name='merge_customer'),
    path('customer/<int:id>/edit/', edit_customer, name='edit_customer'),

    # deleting
    path('delete_number/<int:id_number>', delete_number, name='delete_number'),
    path('delete_whatsApp/<int:id_number>', delete_whatsApp, name='delete_whatsApp'),
    path('delete_landline/<int:id_number>', delete_landline, name='delete_landline'),
    path('delete_email/<int:id_mail>', delete_email, name='delete_email'),
    path('delete_address/<int:id_address>', delete_address, name='delete_address'),
    path('delete_inquiry/<int:id_inq>', delete_inquiry, name='delete_inquiry'),

    # get informations
    path('get_languages', get_languages, name='get_languages'),
    path('get_nationalities', get_nationalities, name='get_nationalities'),
    path('get_sources', get_sources, name='get_sources'),
    path('get_services', get_services, name='get_services'),
    path('get_status', get_status, name='get_status'),
    path('get_services_by_sp/', get_services_by_sp, name='get_services_by_sp'),

    # notifications
    path('notifications', notifications, name='notifications'),
    path('get_notifications/', get_notifications, name='get_notifications'),
    path('get_notify_state/', get_notify_state, name='get_notify_state'),
    path('make_employee_notified/', make_employee_notified, name='make_employee_notified'),

    # messages
    path('messages_list', messages_list, name='messages_list'),
    path('get_messages/', get_messages, name='get_messages'),
    path('get_message_state/', get_message_state, name='get_message_state'),
    path('make_employee_readmessage/', make_employee_readmessage, name='make_employee_readmessage'),


    # inquiries
    path('inquiries_list', inquiries_list, name='inquiries_list'),
    path('inquiry/<int:id>', inquiry_info, name='inquiry_info'),
    path('add_advence/<int:id>', add_advence, name='add_advence'),
    path('make_quotation/<int:id>', make_quotation, name='make_quotation'),
    path('edit_quotation/<int:id>', edit_quotation, name='edit_quotation'),
    path('make_complain/<int:id>', make_complain, name='make_complain'),
    path('messages/<int:id>', messages, name='messages'),
    path('make_booking/<int:id>', make_booking, name='make_booking'),
    path('edit_booking/<int:id>', edit_booking, name='edit_booking'),
    
    # inquiry state
    path('make_inq_underproccess/<int:inq_id>', make_inq_underproccess, name='make_inq_underproccess'),
    path('make_inq_new/<int:inq_id>', make_inq_new, name='make_inq_new'),
    path('make_inq_connecting/<int:inq_id>', make_inq_connecting, name='make_inq_connecting'),
    path('make_inq_sendQ/<int:inq_id>', make_inq_sendQ, name='make_inq_sendQ'),
    path('make_inq_pending/<int:inq_id>', make_inq_pending, name='make_inq_pending'),
    path('make_inq_cancel/<int:inq_id>', make_inq_cancel, name='make_inq_cancel'),
    path('make_inq_complain/<int:inq_id>', make_inq_complain, name='make_inq_complain'),
    path('make_inq_done/<int:inq_id>', make_inq_done, name='make_inq_done'),

]

