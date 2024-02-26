


############### admin manupilations #################
# myapp/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from apps.authentication.models import Employee, Position
from django.http import JsonResponse


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
        position_id = request.POST.get('employee-position')
        username = request.POST.get('employee-username')
        password = request.POST.get('employee-password')


        # Retrieve the selected position
        position = Position.objects.get(id=position_id)

        # Create the employee instance
        employee = Employee.objects.create(
            user=User.objects.create_user(username=username, email=email, password=password),
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            position=position
        )

        return redirect('employee_list')  # Redirect to the employee list page

    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'position': request.user.employee.position,
                'positions':positions,
                'layout_path': layout_path,
                }
    
    context = TemplateLayout.init(request, context)
    return render(request, 'admin/add_employee.html', context)



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
                'emp_name':emp_name
                }

    context = TemplateLayout.init(request, context)
    return render(request, 'admin/employee_list.html', context)
