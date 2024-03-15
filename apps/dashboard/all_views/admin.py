


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
from apps.dashboard.models import Service, SuperProvider


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
        sp = request.POST.get('employee-sp')
        permissions = request.POST.getlist('employee-permissions')
        username = request.POST.get('employee-username')
        password = request.POST.get('employee-password')

        print(permissions)

        # Retrieve the selected position
        if position_name:
            position = Position.objects.get(name=position_name)
        

        if sp:
            service = Service.objects.get(id=sp)
            # Create the employee instance
            employee = Employee.objects.create(
                user=User.objects.create_user(username=username, email=email, password=password),
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                position=position,
                sp_service=service,
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

    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'position': request.user.employee.position,
                'positions':positions,
                'layout_path': layout_path,
                'services':Service.objects.all(),
                'permissions':Permission.objects.all(),
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
        sp_service = request.POST.get('sp-service')

        service = Service.objects.get(id=sp_service)
        new_sp = SuperProvider(
            name = sp_name,
            service = service,
            phone = phone_number,
            email = email
        )
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
        trn = request.POST.get('sp-trn')
        reminder = request.POST.get('service-reminder')
        columns = request.POST.getlist('service-column')
        
        # Convert the list to a comma-separated string
        print(columns)
        not_empty = []
        for c in columns:
            if c != "":
                not_empty.append(c)
        columns_str = ",".join(not_empty)

        # Save the Service instance
        service_instance = Service.objects.create(name=service_name, columns=columns_str, reminder_time=reminder, trn=trn)
        service_instance.save()

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
def services_list_view(request):

    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})

    context = {
        'position': request.user.employee.position,
        'layout_path': layout_path,
        'services':Service.objects.all(),
    }
    context = TemplateLayout.init(request, context)
    return render(request, 'admin/services_list.html',context)
