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
from apps.dashboard.models import (Booking, Inquiry, InvoiceForm, Quotation, QuotationForm,InquiryStatus,
    Service, Status, SuperProvider)
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

    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'title':title,
                'position': request.user.employee.position,
                'layout_path': layout_path,
                'services':Service.objects.all(),
                'permissions':Permission.objects.all(),

                'inquiries_len':inquiries_len,
                'inquiries_len_last':inquiries_len_last,
                'percentage_change':percentage_change,

                'bookings_len':bookings_len,
                'sp_len':sp_len,
                'service_len':service_len,

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

                }
    context = TemplateLayout.init(request, context)
    return render(request, 'dashboard/crm.html', context)

@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['admin']).exists())
def analytics_page(request):
    title = "analytics"

    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'title':title,
                'position': request.user.employee.position,
                'layout_path': layout_path,
                'services':Service.objects.all(),
                'permissions':Permission.objects.all(),
                }
    context = TemplateLayout.init(request, context)
    return render(request, 'dashboard/analytics.html', context)

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
        username = request.POST.get('employee-username')
        password = request.POST.get('employee-password')

        print(permissions)

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
                    sp=sp_company
                )
            else:
                employee = Employee.objects.create(
                    user=User.objects.create_user(username=username, email=email, password=password),
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone_number=phone_number,
                    position=position,
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
        search_count = request.POST.get('search-count')

        print(sp_services)

        new_sp = SuperProvider(
            name = sp_name,
            reference = sp_ref,
            trn=trn,
            search_number = search_count,
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

    context = {'position': request.user.employee.position,
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
        sp = request.POST.get('employee-sp')
        permissions = request.POST.getlist('employee-permissions')
        username = request.POST.get('employee-username')
        password = request.POST.get('employee-password')

        # Retrieve the selected position
        if position_name:
            position = Position.objects.get(name=position_name)

        # Retrieve the selected super provider service
        if sp:
            service = Service.objects.get(id=sp)

        # Retrieve the employee instance
        employee = Employee.objects.get(id=id)

        # Update employee instance with new values
        employee.first_name = first_name
        employee.last_name = last_name
        employee.email = email
        employee.phone_number = phone_number
        employee.position = position
        employee.sp_service = service
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

    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})

    context = {
        'position': request.user.employee.position,
        'layout_path': layout_path,
        'Services': Services,
        'employee': Employee.objects.get(id=id),
        'permissions': Permission.objects.all(),
        'positions': Position.objects.all(),
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
def statistics_view(request):

    # Calculate the date range for the last 30 days
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=29)
    # Query the database to get the counts of inquiries for each date within the last 30 days
    inquiry_counts = defaultdict(int)
    inquiries = Inquiry.objects.filter(date_inq__range=(start_date, end_date))
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
        count = Inquiry.objects.filter(services=service).count()
        services_counter[count] += 1
        services_list.append(service.name)
    services_counts = list(services_counter.keys())




    # Calculate the date range for the last 30 days
    service_colors = {}  # Dictionary to store colors for each service
    random.seed(24)  # Seed the random number generator for reproducibility
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=29)
    # Query the database to get the counts of inquiries for each date and service within the last 30 days
    service_data = defaultdict(lambda: defaultdict(int))
    services = Service.objects.all()
    for service in services:
        inquiries = Inquiry.objects.filter(date_inq__range=(start_date, end_date), services=service)
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
    }
    context = TemplateLayout.init(request, context)

    return render(request, 'admin/statistics/inquiry_statistics.html', context)

