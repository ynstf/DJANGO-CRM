


############### admin manupilations #################
# myapp/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from apps.authentication.models import Employee, Position, Permission
from django.http import JsonResponse
from apps.dashboard.models import InvoiceForm, Quotation, QuotationForm, Service, SuperProvider, Inquiry
from django.shortcuts import render
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
from apps.dashboard.models_com import Service
import random
import json

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
        email = request.POST.get('sp-email')
        phone_number = request.POST.get('sp-phone_number')
        sp_services = request.POST.getlist('sp-service')
        trn = request.POST.get('sp-trn')
        search_count = request.POST.get('search-count')

        print(sp_services)

        new_sp = SuperProvider(
            name = sp_name,
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
            service_instance = Service.objects.create(name=service_name, description=description, columns=columns_str, have_reminder='True', reminder_time=reminder)
            service_instance.save()

        else:
            # Save the Service instance
            service_instance = Service.objects.create(name=service_name, description=description, columns=columns_str, have_reminder='False')
            service_instance.save()
            print(remainder_checked)

        return redirect('services_list')
    
    
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {
        'position': request.user.employee.position,
        'layout_path': layout_path,
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

