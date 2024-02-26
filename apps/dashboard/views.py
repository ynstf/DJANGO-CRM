from web_project import TemplateLayout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render



@login_required(login_url='/')
def dashboard(request):
    # Add the employee's position to the context
    context = {'position': request.user.employee.position}
    context = TemplateLayout.init(request, context)
    return render(request, 'dashboard.html',context)



################# admin ################
from .all_views.admin import add_employee_view,employee_list_view
add_employee = add_employee_view
employee_list = employee_list_view



################# inquiries ###################
from .all_views.inquiries import inquiries_list_view, edit_quotation_view, inquiry_info_view, make_quotation_view, generate_pdf_view
inquiries_list = inquiries_list_view
edit_quotation = edit_quotation_view
inquiry_info = inquiry_info_view
make_quotation = make_quotation_view
generate_pdf = generate_pdf_view


############### get infos ###########
from .all_views.infos import get_languages_view, get_nationalities_view, get_sources_view
get_languages = get_languages_view
get_nationalities = get_nationalities_view
get_sources = get_sources_view


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
from .all_views.customers import customer_list_view, add_customer_view, customer_info_view, edit_customer_view
customer_list = customer_list_view
add_customer = add_customer_view
customer_info = customer_info_view
edit_customer = edit_customer_view