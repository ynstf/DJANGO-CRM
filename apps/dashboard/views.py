import django.urls
from web_project import TemplateLayout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.dashboard.models import InquiryNotify, EmployeeAction, MessageNotify
from django.shortcuts import render





@login_required(login_url='/')
def dashboard(request):
    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()
    messages = MessageNotify.objects.filter(employee=request.user.employee)
    messages_counter = messages.count()

    actions = EmployeeAction.objects.filter(from_employee=request.user.employee).order_by('-update')

    # Add the employee's position to the context
    context = {'position': request.user.employee.position,
            'notifications':notifications,
            'notifications_counter':notifications_counter,
            'actions':actions,
            'messages':messages,
            'messages_counter':messages_counter,
            }
    context = TemplateLayout.init(request, context)
    return render(request, 'dashboard.html',context)

################# admin ################
from .all_views.inquiries import (messages_view,get_message_state_view,
                            make_employee_readmessage_view,get_messages,
                            messages_list_view
                            )

get_message_state = get_message_state_view
make_employee_readmessage = make_employee_readmessage_view
get_messages = get_messages
messages = messages_view
messages_list = messages_list_view


################# admin ################
from .all_views.admin import (add_employee_view,employee_list_view,delete_user_view,
                            employee_info_view,edit_employee_view,add_service_view,
                            services_list_view,add_sp_view,sp_list_view,
                            edit_invoice_doc_view,edit_quotation_doc_view,
                            statistics_view
                            )
add_employee = add_employee_view
employee_list = employee_list_view
delete_user = delete_user_view
employee_info = employee_info_view
edit_employee = edit_employee_view
add_service = add_service_view
services_list = services_list_view
add_sp = add_sp_view
sp_list = sp_list_view
edit_invoice_doc = edit_invoice_doc_view
edit_quotation_doc = edit_quotation_doc_view
statistics = statistics_view




################# booking ###################
from .all_views.booking import (make_booking_view, make_inq_underproccess,
                                generate_invoice_view,edit_booking_view)
make_booking = make_booking_view
make_inq_underproccess = make_inq_underproccess
generate_invoice = generate_invoice_view
edit_booking = edit_booking_view

################# inquiries ###################
from .all_views.inquiries import (inquiries_list_view, edit_quotation_view,
                                    inquiry_info_view, make_quotation_view, 
                                    generate_pdf_view, notifications_view,
                                    get_notifications, make_inq_connecting,
                                    make_inq_sendQ,make_inq_pending,
                                    make_inq_new,get_notify_state_view,
                                    make_employee_notified_view, make_inq_cancel,
                                    add_advence_view, make_complain_view, make_inq_complain,
                                    make_inq_done)

inquiries_list = inquiries_list_view
edit_quotation = edit_quotation_view
inquiry_info = inquiry_info_view
make_quotation = make_quotation_view
generate_pdf = generate_pdf_view
notifications = notifications_view
make_inq_connecting = make_inq_connecting
get_notifications = get_notifications
make_inq_sendQ=make_inq_sendQ
make_inq_pending = make_inq_pending
make_inq_new = make_inq_new
get_notify_state = get_notify_state_view
make_employee_notified = make_employee_notified_view
make_inq_cancel = make_inq_cancel
add_advence = add_advence_view
make_complain = make_complain_view
make_inq_complain = make_inq_complain
make_inq_done = make_inq_done


############### get infos ###########
from .all_views.infos import (get_languages_view, get_nationalities_view,
                                get_sources_view, get_services_view,
                                get_status_view,get_services_by_sp_view)
get_languages = get_languages_view
get_nationalities = get_nationalities_view
get_sources = get_sources_view
get_services = get_services_view
get_status = get_status_view
get_services_by_sp = get_services_by_sp_view


############### delete actions ###############
from .all_views.delete import (
    delete_number_view, delete_whatsApp_view, delete_email_view,
    delete_landline_view, delete_address_view, delete_inquiry_view
)
delete_number = delete_number_view
delete_whatsApp = delete_whatsApp_view
delete_email = delete_email_view
delete_landline = delete_landline_view
delete_address = delete_address_view
delete_inquiry = delete_inquiry_view



############### customer manupilations #################
from .all_views.customers import merge_customer,customer_list_view, add_customer_view, customer_info_view, edit_customer_view
customer_list = customer_list_view
add_customer = add_customer_view
customer_info = customer_info_view
edit_customer = edit_customer_view
merge_customer = merge_customer