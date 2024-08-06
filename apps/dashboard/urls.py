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
                    get_services_by_sp,get_employees_by_sp)

# importation for make inquiry state change
from .views import (make_inq_connecting, make_inq_sendQ, make_inq_sendB,
                    make_inq_pending, make_inq_cancel,
                    make_inq_underproccess, make_inq_new,
                    make_inq_complain, make_inq_done)


from .all_views.admin import crm_page, crm_pdf_view, generate_statistics_pdf, points_admin, add_rate
from .all_views.admin import super_provider, super_provider_edit, service_info,service_edit
from .all_views.chat import chat_page,conversation_view,create_group_view, conversation_group_view,groups_page
from .all_views.inquiries import map,edit_inquiry,make_action, make_approvment, inq_from_points, add_inq_from_points,cancel_point,generatePdf
from .all_views.infos import (check_phone_number, delete_owner_from_inquiry,
                            delete_quotation, delete_customer,delete_inq, check_point_number)
from .all_views.calendar import calendar_view, reminder_day_view
from .all_views.team import points_list_view, point_view, make_point_view
urlpatterns = [
    path('generatePdf/', generatePdf, name='generatePdf'),


    #team leader
    path("points_list/",points_list_view,name="points_list"),
    path("point/<int:id>",point_view,name="point"),
    path("make_point/",make_point_view,name="make_point"),


    #chat
    path("chat_page/",chat_page,name="chat_page"),
    path("groups_page/",groups_page,name="groups_page"),
    path("create_group/",create_group_view,name="create_group_view"),
    path("conversation_group/<int:groupid>",conversation_group_view,name="conversation_group_view"),
    path("conversation/<int:Myid>/<int:Otherid>",conversation_view,name="conversation"),

    #calendar
    path('calendar/', calendar_view, name='calendar_view'),
    path('calendar/<str:date>', reminder_day_view, name='reminder_day_view'),

    #dashboard
    path("dashboard/",dashboard,name="dashboard"),
    path("map/",map,name="map"),
    path("crm_page/",crm_page,name="crm_page"),
    path("crm_pdf/",crm_pdf_view,name="crm_pdf_view"),

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
    path('service_info/<int:id>', service_info, name='service_info'),
    path('service_info/<int:id>/edit', service_edit, name='service_edit'),
    path('statistics/', statistics, name='statistics'),
    path('statistics/pdf/', generate_statistics_pdf, name='statistics_pdf'),
    path('super_provider/<int:id>', super_provider, name='super_provider'),
    path('super_provider/<int:id>/edit', super_provider_edit, name='super_provider_edit'),

    path("points_admin/",points_admin,name="points_admin"),
    path("add_rate/<int:id>",add_rate,name="add_rate"),

    # documents
    path('edit_invoice_doc/', edit_invoice_doc, name='edit_invoice_doc'),
    path('edit_quotation_doc/', edit_quotation_doc, name='edit_quotation_doc'),
    path('generate_pdf/<int:request_id>', generate_pdf, name='generate_pdf'),
    path('generate_invoice/<int:request_id>/', generate_invoice, name='generate_invoice'),

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
    path('delete_customer/<int:id>', delete_customer, name='delete_customer'),
    path('delete_inq/<int:id>', delete_inq, name='delete_inq'),

    # get informations
    path('get_languages', get_languages, name='get_languages'),
    path('get_nationalities', get_nationalities, name='get_nationalities'),
    path('get_sources', get_sources, name='get_sources'),
    path('get_services', get_services, name='get_services'),
    path('get_status', get_status, name='get_status'),
    path('get_services_by_sp/', get_services_by_sp, name='get_services_by_sp'),
    path('get_employees_by_sp/', get_employees_by_sp, name='get_employees_by_sp'),
    path('check-phone-number/', check_phone_number, name='check_phone_number'),
    path('check_point_number/', check_point_number, name='check_point_number'),

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
    path('edit_inquiry/<int:id>', edit_inquiry, name='edit_inquiry'),
    path('make_complain/<int:id>', make_complain, name='make_complain'),
    path('messages/<int:id>', messages, name='messages'),
    path('make_booking/<int:id>', make_booking, name='make_booking'),
    path('edit_booking/<int:id>', edit_booking, name='edit_booking'),
    path('delete_owner_from_inquiry', delete_owner_from_inquiry, name='delete_owner_from_inquiry'),
    path('delete_quotation', delete_quotation, name='delete_quotation'),
    path("from_points/",inq_from_points,name="from_points"),
    path("inq_from_point/<int:id>",add_inq_from_points,name="add_inq_from_points"),
    path("cancel_point/<int:id>",cancel_point,name="cancel_point"),
    
    # inquiry state
    path('make_inq_underproccess/<int:inq_id>', make_inq_underproccess, name='make_inq_underproccess'),
    path('make_inq_new/<int:inq_id>', make_inq_new, name='make_inq_new'),
    path('make_inq_connecting/<int:inq_id>', make_inq_connecting, name='make_inq_connecting'),
    path('make_inq_sendQ/<int:inq_id>', make_inq_sendQ, name='make_inq_sendQ'),
    path('make_inq_sendB/<int:inq_id>', make_inq_sendB, name='make_inq_sendB'),
    path('make_inq_pending/<int:inq_id>', make_inq_pending, name='make_inq_pending'),
    path('make_inq_cancel/<int:inq_id>', make_inq_cancel, name='make_inq_cancel'),
    path('make_inq_complain/<int:inq_id>', make_inq_complain, name='make_inq_complain'),
    path('make_inq_done/<int:inq_id>', make_inq_done, name='make_inq_done'),

    path('make_action/<int:inq_id>', make_action, name='make_action'),

    path('make_approvment/<int:req_id>', make_approvment, name='make_approvment'),

]

