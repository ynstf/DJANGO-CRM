############### admin manupilations #################

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from apps.authentication.models import Employee, Position, Permission
from django.http import JsonResponse
from apps.dashboard.models import (Booking, Complain, Inquiry, InquiryStatus, InvoiceForm,
    Quotation, QuotationForm, Service, Source, Status, SuperProvider)
from django.shortcuts import render
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
from apps.dashboard.models_com import Service
import random
import json


from datetime import datetime, timedelta
from django.contrib import messages
from django.utils.timezone import make_aware
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import io


    
@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['admin']).exists())
def crm_page(request):
    title = "crm"

    
    # Calculate the start and end dates for the last 30 days
    now = make_aware(datetime.now())
    # Calculate the start date for the last 30 days
    start_date = now - timedelta(days=30)
    # Filter inquiries created within the last 30 days
    inquiries_last_30_days = Inquiry.objects.filter(date_inq__range=[start_date, now])
    # Filter inquiries created within the last 30 days
    inquiries_last_30_days = Inquiry.objects.filter(date_inq__range=[start_date, now])
    # Get the count of inquiries for the last 30 days
    inquiries_len = inquiries_last_30_days.count()
    end_date = make_aware(datetime.now()) - timedelta(days=30)
    start_date = end_date - timedelta(days=30)
    inquiries_last_month = Inquiry.objects.filter(date_inq__range=[start_date, end_date])
    inquiries_len_last = inquiries_last_month.count()

    # Calculate the percentage change
    if inquiries_len_last != 0:
        percentage_change = ((inquiries_len - inquiries_len_last) / inquiries_len_last) * 100
    else:
        percentage_change = 0  # Avoid division by zero error



    # Get today's date
    now = datetime.now()
    # Calculate the start and end datetimes for today
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    # Filter inquiries created today
    inquiries_today = Inquiry.objects.filter(date_inq__range=[start_of_day, end_of_day])
    # Get the count of inquiries for today
    inquiries_len_today = inquiries_today.count()


    # Filter inquiries with status of "send Q or B"
    new_status = Status.objects.get(name="new")
    inquiries_today_q_or_b = InquiryStatus.objects.filter(update__range=[start_of_day, end_of_day]).exclude(status=new_status)
    # Get the count of inquiries for today with status "send Q or B"
    inquiries_len_today_q_or_b = inquiries_today_q_or_b.count()
    #bookings_today
    bookings_today = Booking.objects.filter(booking_date__range=[start_of_day, end_of_day]).count()


    # Calculate the start and end dates for the previous day
    # Get the current date and time
    today = datetime.now()

    # Calculate the start and end datetimes for yesterday
    end_of_yesterday = today.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    start_of_yesterday = end_of_yesterday - timedelta(days=1)

    # Filter inquiries created yesterday
    inquiries_yesterday = Inquiry.objects.filter(date_inq__range=[start_of_yesterday, end_of_yesterday])
    actions_yesterday = InquiryStatus.objects.filter(update__range=[start_of_yesterday, end_of_yesterday]).exclude(status=new_status).count()
    bookings_yesterday = Booking.objects.filter(booking_date__range=[start_of_yesterday, end_of_yesterday]).count()


    # Get the count of inquiries for yesterday
    inquiries_len_yesterday = inquiries_yesterday.count()

    # Calculate the percentage change
    if inquiries_len_yesterday != 0:
        percentage_change_today = ((inquiries_len_today - inquiries_len_yesterday) / inquiries_len_yesterday) * 100
    else:
        percentage_change_today = 0  # Avoid division by zero error




    bookings_len = Booking.objects.all().count()
    sp_len = SuperProvider.objects.all().count()
    service_len = Service.objects.all().count()


    all_services = Service.objects.all()
    dic = []
    for service in all_services:
        bookPerService = Booking.objects.filter(booking_service=service).count()
        if bookPerService>0:
            line = {'name':service.name,'books':bookPerService}
            dic.append(line)
    labels_pie = [item['name'] for item in dic]
    numbers_pie = [item['books'] for item in dic]
    # Convert lists to JSON strings
    labels_pie_json = json.dumps(labels_pie)
    numbers_pie_json = json.dumps(numbers_pie)


    inqwithquot = []
    qs = Quotation.objects.all()
    for q in qs:
        if q.inquiry not in inqwithquot:
            inqwithquot.append(q.inquiry)

    quots = []
    for service in all_services:
        quotPerService = Quotation.objects.filter(quotation_service=service).count()
        if quotPerService>0:
            line = {'name':service.name,'books':quotPerService}
            quots.append(line)
    labels_quots_pie = [item['name'] for item in quots]
    numbers_quots_pie = [item['books'] for item in quots]
    # Convert lists to JSON strings
    labels_quots_pie_json = json.dumps(labels_quots_pie)
    numbers_quots_pie_json = json.dumps(numbers_quots_pie)


    dic_prices = []
    bookings_price = 0
    for service in all_services:
        bookPerService = Booking.objects.filter(booking_service=service)
        bookPerServiceCount = Booking.objects.filter(booking_service=service).count()
        price = 0
        for book in bookPerService:
            inquiry = book.inquiry
            quotations = Quotation.objects.filter(inquiry=inquiry)
            for quotation in quotations:
                price += float(quotation.total)
        bookings_price += price
        if bookPerServiceCount>0:
            line = {'name':service.name,'books':price}
            dic_prices.append(line)
    labels_pie_prices = [item['name'] for item in dic_prices]
    numbers_pie_prices = [item['books'] for item in dic_prices]
    # Convert lists to JSON strings
    labels_pie_prices_json = json.dumps(labels_pie_prices)
    numbers_pie_prices_json = json.dumps(numbers_pie_prices)



    quot_prices = []
    quotation_price = 0
    for service in all_services:
        quotationPerService = Quotation.objects.filter(quotation_service=service)
        quotationPerServiceCount = Quotation.objects.filter(quotation_service=service).count()
        price = 0
        for quot in quotationPerService:
            price += float(quot.total)
        quotation_price += price
        if quotationPerServiceCount>0:
            line = {'name':service.name,'books':price}
            quot_prices.append(line)
    labels_pie_quot_prices = [item['name'] for item in quot_prices]
    numbers_pie_quot_prices = [item['books'] for item in quot_prices]
    # Convert lists to JSON strings
    labels_pie_quot_prices_json = json.dumps(labels_pie_quot_prices)
    numbers_pie_quot_prices_json = json.dumps(numbers_pie_quot_prices)



    import random

    # Function to generate a random hex color code
    def generate_random_color():
        return '#{:06x}'.format(random.randint(0, 0xFFFFFF))


    sources = Source.objects.all()
    sources_data = []
    for source in sources:
        inquiries_with_source = Inquiry.objects.filter(source=source).count()
        try:
            percentage = round((inquiries_with_source / Inquiry.objects.all().count()) * 100, 1)
        except:
            percentage = 0.0
        color = generate_random_color()  # Generate a random color for each source
        if inquiries_with_source>0:
            sources_data.append({"name": source.name, "count": inquiries_with_source, "percentage": str(percentage), "color": color})


    try:
        effic = round((bookings_len/Inquiry.objects.all().count())*100,2) 
    except:
        effic = 0.0
        

    #Response time rate
    def to_hours(time_value):
        if isinstance(time_value, timedelta):
            return time_value.total_seconds() / 3600  # Convert timedelta to hours
        elif isinstance(time_value, (int, float)):
            return time_value / 3600  # Assume the int/float is in seconds, convert to hours
        else:
            raise ValueError(f"Unsupported type: {type(time_value)}")

    rates = []
    for sp in SuperProvider.objects.all():
        #levels = ["good","intermidiate","bad","NotInquiry"]
        inquiries = Inquiry.objects.filter(sp=sp)
        mean = 'No Rate'
        level = 'No Data'
        if inquiries.count()==0:
            level = 'No Inquiry'
        else :
            times = []
            for inquiry in inquiries:
                created = inquiry.date_inq
                state = InquiryStatus.objects.get(inquiry=inquiry)
                new = Status.objects.get(name='new')
                if state.status != new:
                    updated = state.update
                    times.append(updated-created)
            # calculate the mean
            if times:
                # Convert all times to hours
                times_in_hours = [to_hours(t) for t in times]
                
                # Calculate mean
                mean = sum(times_in_hours) / len(times_in_hours)

                if mean < 2:
                    level='good'
                if mean >= 2 and mean < 5:
                    level='intermidiate'
                if mean >= 5:
                    level='bad'
                
                print(f"The mean time is: {mean:.2f} hours")
            else:
                print("The list is empty.")


        rates.append({"name":sp.name, "time":mean, "level":level})
    
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'title':title,
                'position': request.user.employee.position,
                'layout_path': layout_path,
                'services':Service.objects.all(),
                'permissions':Permission.objects.all(),

                'all_inq':Inquiry.objects.all().count(),
                'efficiency':effic,
                'complaints':Complain.objects.all().count(),

                'inquiries_len':inquiries_len,
                'inquiries_len_last':inquiries_len_last,
                'percentage_change':percentage_change,

                'bookings_len':bookings_len,
                'sp_len':sp_len,
                'service_len':service_len,

                'dic':dic,
                'labels_pie':labels_pie_json,
                'numbers_pie':numbers_pie_json,

                'quots':quots,
                'labels_pie_quot':labels_quots_pie_json,
                'numbers_pie_quot':numbers_quots_pie_json,
                'inqwithquot':len(inqwithquot),


                'labels_pie_prices':labels_pie_prices_json,
                'numbers_pie_prices':numbers_pie_prices_json,
                'dic_prices':dic_prices,
                'bookings_price':bookings_price,

                'labels_pie_quot_prices':labels_pie_quot_prices_json,
                'numbers_pie_quot_prices':numbers_pie_quot_prices_json,
                'quot_prices':quot_prices,
                'quotation_price':quotation_price,

                'inquiries_len_today':inquiries_len_today,
                'inquiries_len_yesterday':inquiries_len_yesterday,
                'percentage_change_today': percentage_change_today,
                'inquiries_len_today_q_or_b': inquiries_len_today_q_or_b,
                'bookings_today': bookings_today,
                'actions_yesterday':actions_yesterday,
                'bookings_yesterday':bookings_yesterday,

                'sources_data':sources_data,

                'rates':rates
                }
    context = TemplateLayout.init(request, context)
    return render(request, 'dashboard/crm.html', context)



@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['admin']).exists())
def super_provider(request,id):
    title = "super provider info"
    sp = SuperProvider.objects.get(id=id)


    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'title':title,
                'position': request.user.employee.position,
                'layout_path': layout_path,
                'services':Service.objects.all(),
                'permissions':Permission.objects.all(),
                'sp':sp,
                }
    context = TemplateLayout.init(request, context)
    return render(request, 'admin/sp_info.html', context)

@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['admin']).exists())
def super_provider_edit(request,id):
    title = "super provider info"
    sp = SuperProvider.objects.get(id=id)

    if request.method == 'POST':
        # Handle form submission
        sp_name = request.POST.get('sp-name')
        sp_ref = request.POST.get('sp-ref')
        email = request.POST.get('sp-email')
        phone_number = request.POST.get('sp-phone_number')
        sp_services = request.POST.getlist('sp-service')
        trn = request.POST.get('sp-trn')


        print(sp_services)

        # Clear existing services
        sp.service.clear()

        sp.name = sp_name
        sp.reference = sp_ref
        sp.trn = trn
        sp.phone_Number = phone_number
        sp.email = email

        # Add new services
        for service_id in sp_services:
            service = Service.objects.get(id=service_id)
            sp.service.add(service)

        sp.save()

        return redirect('super_provider', id)  # Redirect to the employee list page


    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'title':title,
                'position': request.user.employee.position,
                'layout_path': layout_path,
                'services':Service.objects.all(),
                'permissions':Permission.objects.all(),
                'sp':sp,
                }
    context = TemplateLayout.init(request, context)
    return render(request, 'admin/sp_edit.html', context)
    

@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['admin']).exists())
def add_employee_view(request):
    positions = Position.objects.all()

    if request.method == 'POST':
        # Handle form submission
        first_name = request.POST.get('employee-first_name')
        last_name = request.POST.get('employee-last_name')
        email = request.POST.get('employee-email')
        phone_number = request.POST.get('employee-phone_number')
        position_name = request.POST.get('employee-position')
        #sp = request.POST.get('employee-sp')
        sp_company = request.POST.get('sp_company')
        permissions = request.POST.getlist('employee-permissions')
        search_count = request.POST.get('search-count')
        selected_columns = request.POST.getlist('selected_columns')
        username = request.POST.get('employee-username')
        password = request.POST.get('employee-password')

        print(permissions)
        columns = "*,*".join(selected_columns)
        print(selected_columns)

        # Retrieve the selected position
        if position_name:
            position = Position.objects.get(name=position_name)

        
        users = User.objects.all()
        usernames = [usr.username for usr in users]
        if username not in usernames:
            if sp_company:
                #service = Service.objects.get(id=sp)
                sp_company = SuperProvider.objects.get(id=sp_company)
                
                # Create the employee instance
                employee = Employee.objects.create(
                    user=User.objects.create_user(username=username, email=email, password=password),
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone_number=phone_number,
                    position=position,
                    sp=sp_company,
                    search_number = search_count,
                    columns = columns,
                )
            else:
                employee = Employee.objects.create(
                    user=User.objects.create_user(username=username, email=email, password=password),
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone_number=phone_number,
                    position=position,
                    search_number = search_count,
                    columns = columns,
                )
            # Add permissions to the employee
            for permission_name in permissions:
                permission = Permission.objects.get(name=permission_name)
                employee.permissions.add(permission)
            # Save the employee
            employee.save()

            return redirect('employee_list')  # Redirect to the employee list page
        else:
            messages.error(request, 'This username already exists.')
            return redirect('add_employee')

    all_sp = SuperProvider.objects.all()
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'position': request.user.employee.position,
                'positions':positions,
                'layout_path': layout_path,
                'services':Service.objects.all(),
                'permissions':Permission.objects.all(),
                'all_sp':all_sp
                }
    
    context = TemplateLayout.init(request, context)
    return render(request, 'admin/add_employee.html', context)


@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['admin']).exists())
def add_sp_view(request):

    if request.method == 'POST':
        # Handle form submission
        sp_name = request.POST.get('sp-name')
        sp_ref = request.POST.get('sp-ref')
        email = request.POST.get('sp-email')
        phone_number = request.POST.get('sp-phone_number')
        sp_services = request.POST.getlist('sp-service')
        trn = request.POST.get('sp-trn')




        new_sp = SuperProvider(
            name = sp_name,
            reference = sp_ref,
            trn=trn,
            phone_Number = phone_number,
            email = email,
            )
        new_sp.save()  # Save the SuperProvider object first

        # Add services to the sp
        for sp_service_id in sp_services:
            service = Service.objects.get(id=sp_service_id)
            new_sp.service.add(service)
        new_sp.save()

        return redirect('sp_list')  # Redirect to the employee list page

    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'position': request.user.employee.position,
                'layout_path': layout_path,
                'services':Service.objects.all(),
                'permissions':Permission.objects.all(),
                }
    
    context = TemplateLayout.init(request, context)
    return render(request, 'admin/add_sp.html', context)


@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['admin']).exists())
def sp_list_view(request):
    all_sp = SuperProvider.objects.all()



    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'position': request.user.employee.position,
                'layout_path': layout_path,
                'services':Service.objects.all(),
                'permissions':Permission.objects.all(),
                'all_sp':all_sp
                }
    
    context = TemplateLayout.init(request, context)
    return render(request, 'admin/sp_list.html', context)


@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['admin']).exists())
def employee_list_view(request):
    title = 'employee list'
    employees = Employee.objects.all()

    # Handle search form submission
    if request.method == 'GET':
        emp_name = request.GET.get('emp_name')
        print(emp_name)

        if emp_name:
            employees = employees.filter(first_name__icontains=emp_name)
        

        # If it's an AJAX request, return a JSON response
        if request.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            # Return a JSON response with the employee data
            return JsonResponse({'employees': [{'id': emp.user.id, 'first_name': emp.first_name, 'last_name': emp.last_name, 'email': emp.email, 'phone_number': emp.phone_number, 'position': emp.position.name} for emp in employees]})

    # Render the initial page with the full employee list
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})

    context = { 'title':title,
                'position': request.user.employee.position,
                'layout_path': layout_path,
                'employees': employees,
                'emp_name':emp_name if emp_name!=None else '',
                
                }

    context = TemplateLayout.init(request, context)
    return render(request, 'admin/employee_list.html', context)


@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['admin']).exists())
def delete_user_view(request, id_user):
    user = get_object_or_404(User, id=id_user)
    user.delete()
    return redirect('employee_list')


@user_passes_test(lambda u: u.groups.filter(name__in=['admin']).exists())
@login_required(login_url='/')
def employee_info_view(request, id):
    employee = get_object_or_404(Employee, id=id)

    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'position': request.user.employee.position,
            'layout_path': layout_path,
            'employee': employee,
            }
    context = TemplateLayout.init(request, context)
    return render(request, "admin/employee_info.html", context)


@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['admin']).exists())
def edit_employee_view(request, id):
    if request.method == 'POST':
        # Handle form submission
        first_name = request.POST.get('employee-first_name')
        last_name = request.POST.get('employee-last_name')
        email = request.POST.get('employee-email')
        phone_number = request.POST.get('employee-phone_number')
        position_name = request.POST.get('employee-position')
        sp = request.POST.get('sp_company')
        permissions = request.POST.getlist('employee-permissions')
        search_count = request.POST.get('search-count')
        selected_columns = request.POST.getlist('selected_columns')
        username = request.POST.get('employee-username')
        password = request.POST.get('employee-password')


        columns = "*,*".join(selected_columns)
        print(selected_columns)

        # Retrieve the selected position
        if position_name:
            position = Position.objects.get(name=position_name)



        # Retrieve the employee instance
        employee = Employee.objects.get(id=id)

        # Update employee instance with new values
        employee.first_name = first_name
        employee.last_name = last_name
        employee.email = email
        employee.phone_number = phone_number
        employee.position = position
        employee.search_number = search_count
        employee.columns = columns

        # Retrieve the selected super provider service
        if sp:
            Service_provider = SuperProvider.objects.get(id=sp)
            employee.sp = Service_provider
        
        employee.permissions.set(Permission.objects.filter(name__in=permissions))

        # Update user instance associated with the employee
        usr = User.objects.get(id=employee.user.id)
        if usr.username != username:
            usr.username = username
        if password:
            usr.set_password(password)
        usr.save()


        # Save the changes to the employee instance
        employee.save()

        return redirect('employee_list')  # Redirect to the employee list page

    # If the request is not a POST request, display the edit form
    Services = Service.objects.all()

    columns = []
    if Employee.objects.get(id=id).columns :
        columns = Employee.objects.get(id=id).columns.split("*,*")

    all_columns = ["ids","dates","customer","source","sp","have_media","canceling_causes","advenced_price","total_price","percentage","map"]


    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})

    context = {
        'position': request.user.employee.position,
        'layout_path': layout_path,
        'Services': Services,
        'employee': Employee.objects.get(id=id),
        'permissions': Permission.objects.all(),
        'positions': Position.objects.all(),
        'all_sp':SuperProvider.objects.all(),
        'columns':columns,
        'all_columns':all_columns,
    }
    context = TemplateLayout.init(request, context)
    return render(request, "admin/edit_employee.html", context)


@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['admin']).exists())
def add_service_view(request):
    if request.method == 'POST':
        number_id = request.POST.get('service-number')
        service_name = request.POST.get('service-name')
        description = request.POST.get('service-description')
        
        remainder_checked = request.POST.get('remainder_check')
        reminder = request.POST.get('service-reminder')
        columns = request.POST.getlist('service-column')

        print(remainder_checked)
        
        # Convert the list to a comma-separated string
        print(columns)
        not_empty = []
        for c in columns:
            if c != "":
                not_empty.append(c)
        columns_str = ",".join(not_empty)

        if remainder_checked == "on":
            # Save the Service instance
            service_instance = Service.objects.create(number=number_id, name=service_name, description=description, columns=columns_str, have_reminder='True', reminder_time=reminder)
            service_instance.save()

        else:
            # Save the Service instance
            service_instance = Service.objects.create(number=number_id, name=service_name, description=description, columns=columns_str, have_reminder='False')
            service_instance.save()
            print(remainder_checked)

        return redirect('services_list')
    
    services_id = []
    for srv in Service.objects.all():
        if srv.number:
            services_id.append(srv.number)
    
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {
        'position': request.user.employee.position,
        'layout_path': layout_path,
        'services_id': services_id,
    }
    context = TemplateLayout.init(request, context)
    return render(request, 'admin/add_service.html',context)


@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['admin']).exists())
def edit_invoice_doc_view(request):
    if request.method == 'POST':
        name = request.POST.get('invoive-name')
        image = request.POST.get('invoive-img')
        email = request.POST.get('invoive-email')
        phone = request.POST.get('invoive-phone')

        form, created = InvoiceForm.objects.get_or_create(
            title = name)
        if created :
            form.image = image
            form.email = email
            form.phone = phone
            form.save()
        else :
            form.image = image
            form.email = email
            form.phone = phone
            form.save()


        return redirect('dashboard')

    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    try:
        invoice = InvoiceForm.objects.get(title = 'Invoice1')
    except:
        invoice = ""

    context = {
        'position': request.user.employee.position,
        'layout_path': layout_path,
        'invoice':invoice
    }
    context = TemplateLayout.init(request, context)
    return render(request, 'admin/edit_invoice.html',context)


@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['admin']).exists())
def edit_quotation_doc_view(request):
    if request.method == 'POST':
        name = request.POST.get('quotaion-name')
        image = request.POST.get('quotaion-img')
        email = request.POST.get('quotaion-email')
        phone = request.POST.get('quotaion-phone')


        form, created = QuotationForm.objects.get_or_create(
            title = name)
        if created :
            form.image = image
            form.email = email
            form.phone = phone
            form.save()
        else :
            form.image = image
            form.email = email
            form.phone = phone
            form.save()

        

        return redirect('dashboard')

    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    try:
        quotation = QuotationForm.objects.get(title = 'Quotation1')
    except:
        quotation = ''
    context = {
        'position': request.user.employee.position,
        'layout_path': layout_path,
        'quotation':quotation
    }
    context = TemplateLayout.init(request, context)
    return render(request, 'admin/edit_quotation.html',context)


@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['admin']).exists())
def services_list_view(request):

    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})

    context = {
        'position': request.user.employee.position,
        'layout_path': layout_path,
        'services':Service.objects.all(),
    }
    context = TemplateLayout.init(request, context)
    return render(request, 'admin/services_list.html',context)


@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['admin']).exists())
def service_info(request,id):

    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})

    context = {
        'position': request.user.employee.position,
        'layout_path': layout_path,
        'services':Service.objects.all(),
        'service':Service.objects.get(id=id),
    }
    context = TemplateLayout.init(request, context)
    return render(request, 'admin/service_info.html',context)


@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['admin']).exists())
def service_edit(request,id):
    if request.method == 'POST':
        number_id = request.POST.get('service-number')
        service_name = request.POST.get('service-name')
        description = request.POST.get('service-description')
        
        remainder_checked = request.POST.get('remainder_check')
        reminder = request.POST.get('service-reminder')
        columns = request.POST.getlist('service-column')

        print(remainder_checked)
        
        # Convert the list to a comma-separated string
        print(columns)
        not_empty = []
        for c in columns:
            if c != "":
                not_empty.append(c)
        columns_str = ",".join(not_empty)


        # Fetch the existing Service instance
        this_service = Service.objects.get(id=id)

        # Update the Service instance with new values
        this_service.number = number_id
        this_service.name = service_name
        this_service.description = description
        this_service.columns = columns_str

        # Update the 'have_reminder' field based on the value of remainder_checked
        if remainder_checked == "on":
            this_service.have_reminder = True
            this_service.reminder_time = reminder  # Assuming `reminder` is the field for reminder time
        else:
            this_service.have_reminder = False
            this_service.reminder_time = None  # Reset reminder time if not needed

        # Save the updated Service instance
        this_service.save()


        return redirect('services_list')
    
    services_id = []
    for srv in Service.objects.all():
        if srv.number:
            services_id.append(srv.number)
    
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {
        'position': request.user.employee.position,
        'layout_path': layout_path,
        'services_id': services_id,
        'service': Service.objects.get(id=id),
    }
    context = TemplateLayout.init(request, context)
    return render(request, 'admin/service_edit.html',context)



@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['admin']).exists())
def statistics_view(request):

    status = request.GET.get('status')
    start = request.GET.get('start')
    finish = request.GET.get('finish')
    service = request.GET.get('service')
    sp = request.GET.get('sp')

    # Calculate the date range for the last 30 days
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=29)
    # Query the database to get the counts of inquiries for each date within the last 30 days
    inquiry_counts = defaultdict(int)
    #inquiries = Inquiry.objects.filter(date_inq__range=(start_date, end_date))

    inquiries = Inquiry.objects.all()
    bookings = Booking.objects.all()
    complains = Complain.objects.all()
    inquirystatus = InquiryStatus.objects.all()

    search_str = {}

    if status :
        st = Status.objects.get(id=status)
        inquiries = Inquiry.objects.filter(inquirystatus__status=st)
        bookings = bookings.filter(inquiry__inquirystatus__status=st)
        status=int(status)
        search_str["status"]=status

    if start or finish :
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        finish_date = datetime.strptime(finish, '%Y-%m-%d').date()
        inquiries = inquiries.filter(date_inq__range=[start_date, finish_date])
        bookings = bookings.filter(booking_date__range=[start_date, finish_date])
        complains = complains.filter(opened__range=[start_date, finish_date])
        inquirystatus = inquirystatus.filter(update__range=[start_date, finish_date])
        
    
    if service :
        inquiries = inquiries.filter(services=service)
        bookings = bookings.filter(booking_service=service)
        complains = Complain.objects.filter(inquiry__services=service)
        service = int(service)
        search_str["service"]=service
    
    if sp :
        inquiries = inquiries.filter(sp=sp)
        bookings = bookings.filter(inquiry__sp=sp)
        complains = Complain.objects.filter(inquiry__sp=sp)
        inquirystatus = inquirystatus.filter(inquiry__sp=sp)
        sp = int(sp)
        search_str["sp"]=sp
    


    # Calculate the start and end dates for the last 30 days
    now = make_aware(datetime.now())
    # Calculate the start date for the last 30 days
    st_date = now - timedelta(days=30)
    # Filter inquiries created within the last 30 days
    inquiries_last_30_days = inquiries.filter(date_inq__range=[st_date, now])
    # Get the count of inquiries for the last 30 days
    inquiries_len_30 = inquiries_last_30_days.count()
    end_date = make_aware(datetime.now()) - timedelta(days=30)
    st_date = end_date - timedelta(days=30)
    inquiries_last_month = inquiries.filter(date_inq__range=[st_date, end_date])
    inquiries_len_last_30 = inquiries_last_month.count()
    # Calculate the percentage change
    if inquiries_len_last_30 != 0:
        percentage_change = ((inquiries_len_30 - inquiries_len_last_30) / inquiries_len_last_30) * 100

    else:
        percentage_change = float('inf')  # Handle the case where last month's inquiries are zero to avoid division by zero



    # Get today's date
    now = datetime.now()
    # Calculate the start and end datetimes for today
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    # Filter inquiries created today
    inquiries_today = inquiries.filter(date_inq__range=[start_of_day, end_of_day])
    # Get the count of inquiries for today
    inquiries_len_today = inquiries_today.count()


    # Filter inquiries with status of "send Q or B"
    new_status = Status.objects.get(name="new")
    inquiries_today_q_or_b = inquirystatus.filter(update__range=[start_of_day, end_of_day]).exclude(status=new_status)
    # Get the count of inquiries for today with status "send Q or B"
    inquiries_len_today_q_or_b = inquiries_today_q_or_b.count()
    #bookings_today
    bookings_today = bookings.filter(booking_date__range=[start_of_day, end_of_day]).count()


    # Calculate the start and end dates for the previous day
    # Get the current date and time
    today = datetime.now()
    # Calculate the start and end datetimes for yesterday
    end_of_yesterday = today.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    start_of_yesterday = end_of_yesterday - timedelta(days=1)
    # Filter inquiries created yesterday
    inquiries_yesterday = inquiries.filter(date_inq__range=[start_of_yesterday, end_of_yesterday])
    actions_yesterday = inquirystatus.filter(update__range=[start_of_yesterday, end_of_yesterday]).exclude(status=new_status).count()
    bookings_yesterday = bookings.filter(booking_date__range=[start_of_yesterday, end_of_yesterday]).count()
    # Get the count of inquiries for yesterday
    inquiries_len_yesterday = inquiries_yesterday.count()


    # Calculate the percentage change
    if inquiries_len_yesterday != 0:
        percentage_change_today = ((inquiries_len_today - inquiries_len_yesterday) / inquiries_len_yesterday) * 100
    else:
        percentage_change_today = 0  # Avoid division by zero error



    all_services = Service.objects.all()
    dic = []
    for service in all_services:
        bookPerService = bookings.filter(booking_service=service).count()
        if bookPerService>0:
            line = {'name':service.name,'books':bookPerService}
            dic.append(line)
    labels_pie = [item['name'] for item in dic]
    numbers_pie = [item['books'] for item in dic]
    # Convert lists to JSON strings
    labels_pie_json = json.dumps(labels_pie)
    numbers_pie_json = json.dumps(numbers_pie)


    dic_prices = []
    bookings_price = 0
    for service in all_services:
        bookPerService = bookings.filter(booking_service=service)
        bookPerServiceCount = bookings.filter(booking_service=service).count()
        price = 0
        for book in bookPerService:
            inquiry = book.inquiry
            quotations = Quotation.objects.filter(inquiry=inquiry)
            for quotation in quotations:
                price += float(quotation.total)
        bookings_price += price
        if bookPerServiceCount>0:
            line = {'name':service.name,'books':price}
            dic_prices.append(line)
    labels_pie_prices = [item['name'] for item in dic_prices]
    numbers_pie_prices = [item['books'] for item in dic_prices]
    # Convert lists to JSON strings
    labels_pie_prices_json = json.dumps(labels_pie_prices)
    numbers_pie_prices_json = json.dumps(numbers_pie_prices)



    import random
    # Function to generate a random hex color code
    def generate_random_color():
        return '#{:06x}'.format(random.randint(0, 0xFFFFFF))


    sources = Source.objects.all()
    sources_data = []
    for source in sources:
        inquiries_with_source = inquiries.filter(source=source).count()
        try:
            percentage = round((inquiries_with_source / inquiries.all().count()) * 100, 1)
        except:
            percentage = 0.0
        color = generate_random_color()  # Generate a random color for each source
        if inquiries_with_source>0:
            sources_data.append({"name": source.name, "count": inquiries_with_source, "percentage": str(percentage), "color": color})





    inquiries_len_last = inquiries.count()
    bookings_len_last = bookings.count()

    try:
        effic = round((bookings_len_last/inquiries_len_last)*100,2) 
    except:
        effic = 0.0

    complains = complains.count()
    








    ##############################################################

    status = request.GET.get('status')
    start = request.GET.get('start')
    finish = request.GET.get('finish')
    service = request.GET.get('service')
    sp = request.GET.get('sp')

    # Calculate the date range for the last 30 days
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=29)
    # Query the database to get the counts of inquiries for each date within the last 30 days
    inquiry_counts = defaultdict(int)
    #inquiries = Inquiry.objects.filter(date_inq__range=(start_date, end_date))



    inquiries = Inquiry.objects.all()


    if status :
        st = Status.objects.get(id=status)
        inquiries = Inquiry.objects.filter(inquirystatus__status=st)


    if start or finish :
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        finish_date = datetime.strptime(finish, '%Y-%m-%d').date()
        inquiries = inquiries.filter(date_inq__range=[start_date, finish_date])

        
    
    if service :
        inquiries = inquiries.filter(services=service)

    
    if sp :
        inquiries = inquiries.filter(sp=sp)



    for inquiry in inquiries:
        inquiry_date = inquiry.date_inq.strftime('%Y-%m-%d')
        inquiry_counts[inquiry_date] += 1
    # Prepare the data for the chart
    dates = list(inquiry_counts.keys())
    counts = list(inquiry_counts.values())
    # Sort dates chronologically
    dates.sort()


    # Calculate the date range of each service for the last 30 days
    services = Service.objects.all()
    services_list = []
    services_counter = defaultdict(int)
    for service in services:
        count = inquiries.filter(services=service).count()
        services_counter[count] += 1
        services_list.append(service.name)
    services_counts = list(services_counter.keys())



    """
    # Calculate the date range for the last 30 days
    service_colors = {}  # Dictionary to store colors for each service
    import random
    random.seed(24)  # Seed the random number generator for reproducibility

    # Query the database to get the counts of inquiries for each date and service within the last 30 days
    service_data = defaultdict(lambda: defaultdict(int))
    services = Service.objects.all()
    for service in services:
        inquiries = inquiries.filter(date_inq__range=(start_date, end_date), services=service)
        for inquiry in inquiries:
            inquiry_date = inquiry.date_inq.strftime('%Y-%m-%d')
            service_data[inquiry_date][service.name] += 1
    # Prepare the aggregated data for the chart
    dates = sorted(service_data.keys())
    service_names = [service.name for service in services]
    service_counts = {service: [] for service in service_names}
    colors = ["31, 119, 180","255, 127, 14","44, 160, 44","214, 39, 40","148, 103, 189","140, 86, 75","227, 119, 194","127, 127, 127","188, 189, 34","23, 190, 207","26, 85, 255","255, 0, 191","128, 255, 0","255, 191, 0","0, 255, 204"]
    
    for date in dates:
        color_counter = 0
        for service in service_names:
            service_counts[service].append(service_data[date][service])
            rgb_values = [random.randint(0, 255) for _ in range(3)]
            rgb_string = ', '.join(map(str, rgb_values))
            #service_colors[service] = rgb_string
            service_colors[service] = colors[color_counter]
            color_counter+=1
            #print(service_names,colors[color_counter])
            
    
    # Convert the service_colors dictionary to a JSON object
    service_colors_json = json.dumps(service_colors)
    print(service_colors_json)
    """
    # Calculate the date range for the last 30 days
    service_colors = {}  # Dictionary to store colors for each service
    random.seed(24)  # Seed the random number generator for reproducibility

    # Query the database to get the counts of inquiries for each date and service within the last 30 days
    service_data = defaultdict(lambda: defaultdict(int))
    services = Service.objects.all()


    for service in services:
        inquiries = inquiries.filter(date_inq__range=(start_date, end_date), services=service)
        for inquiry in inquiries:
            inquiry_date = inquiry.date_inq.strftime('%Y-%m-%d')
            service_data[inquiry_date][service.name] += 1

    # Prepare the aggregated data for the chart
    dates = sorted(service_data.keys())
    service_names = [service.name for service in services]
    service_counts = {service: [] for service in service_names}
    colors = ["31, 119, 180", "255, 127, 14", "44, 160, 44", "214, 39, 40", "148, 103, 189", "140, 86, 75", "227, 119, 194", "127, 127, 127", "188, 189, 34", "23, 190, 207", "26, 85, 255", "255, 0, 191", "128, 255, 0", "255, 191, 0", "0, 255, 204"]

    # Assign colors to services
    for index, service in enumerate(service_names):
        service_colors[service] = colors[index % len(colors)]

    # Fill service_counts for each date
    for date in dates:
        for service in service_names:
            service_counts[service].append(service_data[date][service])

    # Convert the service_colors dictionary to a JSON object
    service_colors_json = json.dumps(service_colors)
    print(service_colors_json)

    ################################################################################

























    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {
        'position': request.user.employee.position,
        'layout_path': layout_path,
        'dates': dates,
        'counts': counts,
        'service_counts': service_counts,
        'services_list': services_list,
        'services_counts': services_counts,
        'service_colors_json': service_colors_json,
        'services':Service.objects.all(),
        'states':Status.objects.all(),
        'service_providers':SuperProvider.objects.all(),
        'search_str':search_str,

        'inquiries_len_last':inquiries_len_last,
        'bookings_len_last':bookings_len_last,
        'efficiency':effic,
        'complaints':complains,
        'inquiries_len':inquiries_len_30,
        'inquiries_len_last_30':inquiries_len_last_30,
        'percentage_change':percentage_change,

        'inquiries_len_today':inquiries_len_today,
        'percentage_change_today':percentage_change_today,
        'inquiries_len_today_q_or_b':inquiries_len_today_q_or_b,
        'bookings_today':bookings_today,

        'inquiries_len_yesterday':inquiries_len_yesterday,
        'actions_yesterday':actions_yesterday,
        'bookings_yesterday':bookings_yesterday,

        'dic':dic,
        'labels_pie':labels_pie_json,
        'numbers_pie':numbers_pie_json,

        'labels_pie_prices':labels_pie_prices_json,
        'numbers_pie_prices':numbers_pie_prices_json,
        'dic_prices':dic_prices,
        'bookings_price':bookings_price,

        
        'sources_data':sources_data,





    }
    context = TemplateLayout.init(request, context)

    return render(request, 'admin/statistics/inquiry_statistics.html', context)



def generate_statistics_pdf(request):
    # Get parameters from request
    status = request.GET.get('status', '')
    start = request.GET.get('start', '')
    finish = request.GET.get('finish', '')
    service = request.GET.get('service', '')
    sp = request.GET.get('sp', '')




    # Calculate the date range for the last 30 days
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=29)
    # Query the database to get the counts of inquiries for each date within the last 30 days
    inquiry_counts = defaultdict(int)
    #inquiries = Inquiry.objects.filter(date_inq__range=(start_date, end_date))

    inquiries = Inquiry.objects.all()
    bookings = Booking.objects.all()
    complains = Complain.objects.all()
    inquirystatus = InquiryStatus.objects.all()

    search_str = {}

    if status :
        st = Status.objects.get(id=status)
        inquiries = Inquiry.objects.filter(inquirystatus__status=st)
        bookings = bookings.filter(inquiry__inquirystatus__status=st)
        status=int(status)
        search_str["status"]=status

    if start or finish :
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        finish_date = datetime.strptime(finish, '%Y-%m-%d').date()
        inquiries = inquiries.filter(date_inq__range=[start_date, finish_date])
        bookings = bookings.filter(booking_date__range=[start_date, finish_date])
        complains = complains.filter(opened__range=[start_date, finish_date])
        inquirystatus = inquirystatus.filter(update__range=[start_date, finish_date])
        
    
    if service :
        inquiries = inquiries.filter(services=service)
        bookings = bookings.filter(booking_service=service)
        complains = Complain.objects.filter(inquiry__services=service)
        service = int(service)
        search_str["service"]=service
    
    if sp :
        inquiries = inquiries.filter(sp=sp)
        bookings = bookings.filter(inquiry__sp=sp)
        complains = Complain.objects.filter(inquiry__sp=sp)
        inquirystatus = inquirystatus.filter(inquiry__sp=sp)
        sp = int(sp)
        search_str["sp"]=sp
    


    # Calculate the start and end dates for the last 30 days
    now = make_aware(datetime.now())
    # Calculate the start date for the last 30 days
    st_date = now - timedelta(days=30)
    # Filter inquiries created within the last 30 days
    inquiries_last_30_days = inquiries.filter(date_inq__range=[st_date, now])
    # Get the count of inquiries for the last 30 days
    inquiries_len_30 = inquiries_last_30_days.count()
    end_date = make_aware(datetime.now()) - timedelta(days=30)
    st_date = end_date - timedelta(days=30)
    inquiries_last_month = inquiries.filter(date_inq__range=[st_date, end_date])
    inquiries_len_last_30 = inquiries_last_month.count()
    # Calculate the percentage change
    if inquiries_len_last_30 != 0:
        percentage_change = ((inquiries_len_30 - inquiries_len_last_30) / inquiries_len_last_30) * 100

    else:
        percentage_change = float('inf')  # Handle the case where last month's inquiries are zero to avoid division by zero



    # Get today's date
    now = datetime.now()
    # Calculate the start and end datetimes for today
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    # Filter inquiries created today
    inquiries_today = inquiries.filter(date_inq__range=[start_of_day, end_of_day])
    # Get the count of inquiries for today
    inquiries_len_today = inquiries_today.count()


    # Filter inquiries with status of "send Q or B"
    new_status = Status.objects.get(name="new")
    inquiries_today_q_or_b = inquirystatus.filter(update__range=[start_of_day, end_of_day]).exclude(status=new_status)
    # Get the count of inquiries for today with status "send Q or B"
    inquiries_len_today_q_or_b = inquiries_today_q_or_b.count()
    #bookings_today
    bookings_today = bookings.filter(booking_date__range=[start_of_day, end_of_day]).count()


    # Calculate the start and end dates for the previous day
    # Get the current date and time
    today = datetime.now()
    # Calculate the start and end datetimes for yesterday
    end_of_yesterday = today.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    start_of_yesterday = end_of_yesterday - timedelta(days=1)
    # Filter inquiries created yesterday
    inquiries_yesterday = inquiries.filter(date_inq__range=[start_of_yesterday, end_of_yesterday])
    actions_yesterday = inquirystatus.filter(update__range=[start_of_yesterday, end_of_yesterday]).exclude(status=new_status).count()
    bookings_yesterday = bookings.filter(booking_date__range=[start_of_yesterday, end_of_yesterday]).count()
    # Get the count of inquiries for yesterday
    inquiries_len_yesterday = inquiries_yesterday.count()


    # Calculate the percentage change
    if inquiries_len_yesterday != 0:
        percentage_change_today = ((inquiries_len_today - inquiries_len_yesterday) / inquiries_len_yesterday) * 100
    else:
        percentage_change_today = 0  # Avoid division by zero error



    all_services = Service.objects.all()
    dic = []
    for service in all_services:
        bookPerService = bookings.filter(booking_service=service).count()
        if bookPerService>0:
            line = {'name':service.name,'books':bookPerService}
            dic.append(line)
    labels_pie = [item['name'] for item in dic]
    numbers_pie = [item['books'] for item in dic]
    # Convert lists to JSON strings
    labels_pie_json = json.dumps(labels_pie)
    numbers_pie_json = json.dumps(numbers_pie)


    dic_prices = []
    bookings_price = 0
    for service in all_services:
        bookPerService = bookings.filter(booking_service=service)
        bookPerServiceCount = bookings.filter(booking_service=service).count()
        price = 0
        for book in bookPerService:
            inquiry = book.inquiry
            quotations = Quotation.objects.filter(inquiry=inquiry)
            for quotation in quotations:
                price += float(quotation.total)
        bookings_price += price
        if bookPerServiceCount>0:
            line = {'name':service.name,'books':price}
            dic_prices.append(line)
    labels_pie_prices = [item['name'] for item in dic_prices]
    numbers_pie_prices = [item['books'] for item in dic_prices]
    # Convert lists to JSON strings
    labels_pie_prices_json = json.dumps(labels_pie_prices)
    numbers_pie_prices_json = json.dumps(numbers_pie_prices)



    import random
    # Function to generate a random hex color code
    def generate_random_color():
        return '#{:06x}'.format(random.randint(0, 0xFFFFFF))


    sources = Source.objects.all()
    sources_data = []
    for source in sources:
        inquiries_with_source = inquiries.filter(source=source).count()
        try:
            percentage = round((inquiries_with_source / inquiries.all().count()) * 100, 1)
        except:
            percentage = 0.0
        color = generate_random_color()  # Generate a random color for each source
        if inquiries_with_source>0:
            sources_data.append({"name": source.name, "count": inquiries_with_source, "percentage": str(percentage), "color": color})





    inquiries_len_last = inquiries.count()
    bookings_len_last = bookings.count()

    try:
        effic = round((bookings_len_last/inquiries_len_last)*100,2) 
    except:
        effic = 0.0

    complains = complains.count()








    this_sp= SuperProvider.objects.get(id=request.GET.get('sp', '')).name if request.GET.get('sp', '').isdigit() and SuperProvider.objects.filter(id=request.GET.get('sp', '')).exists() else None,
    this_first=request.GET.get('start', ''),
    this_end=request.GET.get('finish', ''),
    this_service= Service.objects.get(id=request.GET.get('service', '')).name if request.GET.get('service', '').isdigit() and Service.objects.filter(id=request.GET.get('service', '')).exists() else None,                
    this_status=Status.objects.get(id=request.GET.get('status', '')).name if request.GET.get('status', '').isdigit() and Status.objects.filter(id=request.GET.get('status', '')).exists() else None,


    # Create a PDF template using Django template
    template_path = 'dashboard/statistics_pdf.html'  # Create a template for your PDF
    template = get_template(template_path)

    try:
        sp = QuotationForm.objects.get(title = 'Quotation1')
    except:
        sp = ''
    
    context = {
                'position': request.user.employee.position,
                'sp':sp,
                'date':datetime.today(),
                'user':request.user,

                'services':Service.objects.all(),
                'permissions':Permission.objects.all(),

                'all_inq':Inquiry.objects.all().count(),


                'inquiries_len_last':inquiries_len_last,
                'bookings_len_last':bookings_len_last,
                'bookings_len':bookings_len_last,
                'efficiency':effic,
                'complaints':complains,
                'inquiries_len':inquiries_len_30,
                'inquiries_len_last_30':inquiries_len_last_30,
                'percentage_change':percentage_change,



                'dic':dic,
                'labels_pie':labels_pie_json,
                'numbers_pie':numbers_pie_json,




                'labels_pie_prices':labels_pie_prices_json,
                'numbers_pie_prices':numbers_pie_prices_json,
                'dic_prices':dic_prices,
                'bookings_price':bookings_price,



                'inquiries_len_today':inquiries_len_today,
                'inquiries_len_yesterday':inquiries_len_yesterday,
                'percentage_change_today': percentage_change_today,
                'inquiries_len_today_q_or_b': inquiries_len_today_q_or_b,
                'bookings_today': bookings_today,
                'actions_yesterday':actions_yesterday,
                'bookings_yesterday':bookings_yesterday,

                'sources_data':sources_data,
                
                'this_sp': SuperProvider.objects.get(id=request.GET.get('sp', '')) if request.GET.get('sp', '').isdigit() and SuperProvider.objects.filter(id=request.GET.get('sp', '')).exists() else None,
                'this_first':request.GET.get('start', ''),
                'this_end':request.GET.get('finish', ''),
                'this_service': Service.objects.get(id=request.GET.get('service', '')) if request.GET.get('service', '').isdigit() and Service.objects.filter(id=request.GET.get('service', '')).exists() else None,                
                'this_status':Status.objects.get(id=request.GET.get('status', '')) if request.GET.get('status', '').isdigit() and Status.objects.filter(id=request.GET.get('status', '')).exists() else None,

                }


    html_content = template.render(context)
    # Create a PDF file using ReportLab
    pdf_file = io.BytesIO()
    pisa.CreatePDF(html_content, dest=pdf_file)
    # Set response content type
    response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')
    # Set the filename for download
    response['Content-Disposition'] = f'inline; filename="crm_statistic_sp:{this_sp}_From:{this_first}To:{this_end}_Service:{this_service}_Status:{this_status}.pdf"'


    return response


def crm_pdf_view(request):

    title = "crm"

    
    # Calculate the start and end dates for the last 30 days
    now = make_aware(datetime.now())
    # Calculate the start date for the last 30 days
    start_date = now - timedelta(days=30)
    # Filter inquiries created within the last 30 days
    inquiries_last_30_days = Inquiry.objects.filter(date_inq__range=[start_date, now])
    # Filter inquiries created within the last 30 days
    inquiries_last_30_days = Inquiry.objects.filter(date_inq__range=[start_date, now])
    # Get the count of inquiries for the last 30 days
    inquiries_len = inquiries_last_30_days.count()
    end_date = make_aware(datetime.now()) - timedelta(days=30)
    start_date = end_date - timedelta(days=30)
    inquiries_last_month = Inquiry.objects.filter(date_inq__range=[start_date, end_date])
    inquiries_len_last = inquiries_last_month.count()

    # Calculate the percentage change
    if inquiries_len_last != 0:
        percentage_change = round(((inquiries_len - inquiries_len_last) / inquiries_len_last) * 100,2)
    else:
        percentage_change = 0  # Avoid division by zero error



    # Get today's date
    now = datetime.now()
    # Calculate the start and end datetimes for today
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    # Filter inquiries created today
    inquiries_today = Inquiry.objects.filter(date_inq__range=[start_of_day, end_of_day])
    # Get the count of inquiries for today
    inquiries_len_today = inquiries_today.count()


    # Filter inquiries with status of "send Q or B"
    new_status = Status.objects.get(name="new")
    inquiries_today_q_or_b = InquiryStatus.objects.filter(update__range=[start_of_day, end_of_day]).exclude(status=new_status)
    # Get the count of inquiries for today with status "send Q or B"
    inquiries_len_today_q_or_b = inquiries_today_q_or_b.count()
    #bookings_today
    bookings_today = Booking.objects.filter(booking_date__range=[start_of_day, end_of_day]).count()


    # Calculate the start and end dates for the previous day
    # Get the current date and time
    today = datetime.now()

    # Calculate the start and end datetimes for yesterday
    end_of_yesterday = today.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    start_of_yesterday = end_of_yesterday - timedelta(days=1)

    # Filter inquiries created yesterday
    inquiries_yesterday = Inquiry.objects.filter(date_inq__range=[start_of_yesterday, end_of_yesterday])
    actions_yesterday = InquiryStatus.objects.filter(update__range=[start_of_yesterday, end_of_yesterday]).exclude(status=new_status).count()
    bookings_yesterday = Booking.objects.filter(booking_date__range=[start_of_yesterday, end_of_yesterday]).count()


    # Get the count of inquiries for yesterday
    inquiries_len_yesterday = inquiries_yesterday.count()

    # Calculate the percentage change
    if inquiries_len_yesterday != 0:
        percentage_change_today = ((inquiries_len_today - inquiries_len_yesterday) / inquiries_len_yesterday) * 100
    else:
        percentage_change_today = 0  # Avoid division by zero error




    bookings_len = Booking.objects.all().count()
    sp_len = SuperProvider.objects.all().count()
    service_len = Service.objects.all().count()


    all_services = Service.objects.all()
    dic = []
    for service in all_services:
        bookPerService = Booking.objects.filter(booking_service=service).count()
        if bookPerService>0:
            line = {'name':service.name,'books':bookPerService}
            dic.append(line)
    labels_pie = [item['name'] for item in dic]
    numbers_pie = [item['books'] for item in dic]
    # Convert lists to JSON strings
    labels_pie_json = json.dumps(labels_pie)
    numbers_pie_json = json.dumps(numbers_pie)


    inqwithquot = []
    qs = Quotation.objects.all()
    for q in qs:
        if q.inquiry not in inqwithquot:
            inqwithquot.append(q.inquiry)

    quots = []
    for service in all_services:
        quotPerService = Quotation.objects.filter(quotation_service=service).count()
        if quotPerService>0:
            line = {'name':service.name,'books':quotPerService}
            quots.append(line)
    labels_quots_pie = [item['name'] for item in quots]
    numbers_quots_pie = [item['books'] for item in quots]
    # Convert lists to JSON strings
    labels_quots_pie_json = json.dumps(labels_quots_pie)
    numbers_quots_pie_json = json.dumps(numbers_quots_pie)


    dic_prices = []
    bookings_price = 0
    for service in all_services:
        bookPerService = Booking.objects.filter(booking_service=service)
        bookPerServiceCount = Booking.objects.filter(booking_service=service).count()
        price = 0
        for book in bookPerService:
            inquiry = book.inquiry
            quotations = Quotation.objects.filter(inquiry=inquiry)
            for quotation in quotations:
                price += float(quotation.total)
        bookings_price += price
        if bookPerServiceCount>0:
            line = {'name':service.name,'books':price}
            dic_prices.append(line)
    labels_pie_prices = [item['name'] for item in dic_prices]
    numbers_pie_prices = [item['books'] for item in dic_prices]
    # Convert lists to JSON strings
    labels_pie_prices_json = json.dumps(labels_pie_prices)
    numbers_pie_prices_json = json.dumps(numbers_pie_prices)



    quot_prices = []
    quotation_price = 0
    for service in all_services:
        quotationPerService = Quotation.objects.filter(quotation_service=service)
        quotationPerServiceCount = Quotation.objects.filter(quotation_service=service).count()
        price = 0
        for quot in quotationPerService:
            inquiry = quot.inquiry
            quotations = Quotation.objects.filter(inquiry=inquiry)
            for quotation in quotations:
                price += float(quotation.total)
        quotation_price += price
        if quotationPerServiceCount>0:
            line = {'name':service.name,'books':price}
            quot_prices.append(line)
    labels_pie_quot_prices = [item['name'] for item in quot_prices]
    numbers_pie_quot_prices = [item['books'] for item in quot_prices]
    # Convert lists to JSON strings
    labels_pie_quot_prices_json = json.dumps(labels_pie_quot_prices)
    numbers_pie_quot_prices_json = json.dumps(numbers_pie_quot_prices)



    import random

    # Function to generate a random hex color code
    def generate_random_color():
        return '#{:06x}'.format(random.randint(0, 0xFFFFFF))


    sources = Source.objects.all()
    sources_data = []
    for source in sources:
        inquiries_with_source = Inquiry.objects.filter(source=source).count()
        try:
            percentage = round((inquiries_with_source / Inquiry.objects.all().count()) * 100, 1)
        except:
            percentage = 0.0
        color = generate_random_color()  # Generate a random color for each source
        if inquiries_with_source>0:
            sources_data.append({"name": source.name, "count": inquiries_with_source, "percentage": str(percentage), "color": color})


    try:
        effic = round((bookings_len/Inquiry.objects.all().count())*100,2) 
    except:
        effic = 0.0


    # Create a PDF template using Django template
    template_path = 'dashboard/crm_pdf.html'  # Create a template for your PDF
    template = get_template(template_path)

    try:
        sp = QuotationForm.objects.get(title = 'Quotation1')
    except:
        sp = ''

    
    context = {'title':title,
                'position': request.user.employee.position,
                'sp':sp,
                'date':datetime.today(),
                'user':request.user,

                'services':Service.objects.all(),
                'permissions':Permission.objects.all(),

                'all_inq':Inquiry.objects.all().count(),
                'efficiency':effic,
                'complaints':Complain.objects.all().count(),

                'inquiries_len':inquiries_len,
                'inquiries_len_last':inquiries_len_last,
                'percentage_change':percentage_change,

                'bookings_len':bookings_len,
                'sp_len':sp_len,
                'service_len':service_len,

                'dic':dic,
                'labels_pie':labels_pie_json,
                'numbers_pie':numbers_pie_json,

                'quots':quots,
                'labels_pie_quot':labels_quots_pie_json,
                'numbers_pie_quot':numbers_quots_pie_json,
                'inqwithquot':len(inqwithquot),


                'labels_pie_prices':labels_pie_prices_json,
                'numbers_pie_prices':numbers_pie_prices_json,
                'dic_prices':dic_prices,
                'bookings_price':bookings_price,

                'labels_pie_quot_prices':labels_pie_quot_prices_json,
                'numbers_pie_quot_prices':numbers_pie_quot_prices_json,
                'quot_prices':quot_prices,
                'quotation_price':quotation_price,

                'inquiries_len_today':inquiries_len_today,
                'inquiries_len_yesterday':inquiries_len_yesterday,
                'percentage_change_today': percentage_change_today,
                'inquiries_len_today_q_or_b': inquiries_len_today_q_or_b,
                'bookings_today': bookings_today,
                'actions_yesterday':actions_yesterday,
                'bookings_yesterday':bookings_yesterday,

                'sources_data':sources_data,

                }
    html_content = template.render(context)

    # Create a PDF file using ReportLab
    pdf_file = io.BytesIO()
    pisa.CreatePDF(html_content, dest=pdf_file)

    # Set response content type
    response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')

    # Set the filename for download
    response['Content-Disposition'] = 'inline; filename="crm_statistic.pdf"'

    return response

