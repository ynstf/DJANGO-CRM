import django.contrib
import django.db
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.template.loader import get_template
from web_project.template_helpers.theme import TemplateHelper
from web_project import TemplateLayout
from xhtml2pdf import pisa
import io
from apps.dashboard.models_com import SuperProvider
from apps.dashboard.views import employee_info
from ..models import Inquiry, Quotation, QuotationForm, Customer, PhoneNumber, Email, Service, Booking
from apps.authentication.models import Employee, Permission, Position
from apps.dashboard.models import (EmployeeAction, Inquiry, InquiryNotify, InquiryReminder,
    InquiryStatus, IsEmployeeNotified, Language, Nationality, Quotation, Source, Status, Request,
    SuperProvider)
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.urls import reverse
from urllib.parse import quote
from datetime import timedelta
from apps.dashboard.models import Points, QuotationForm, Advence, Invoice, Complain, Message, MessageNotify, IsEmployeeReadMessage
import cloudinary
import cloudinary.uploader
import json
from datetime import datetime
from django.contrib import messages as msgs
from django.db.models import Q
from django.utils import timezone

@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['team_leader']).exists() )
def points_list_view(request):
    


    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()
    messages = MessageNotify.objects.filter(employee=request.user.employee)
    messages_counter = messages.count()



    # Handle search form submission
    if request.method == 'GET':

        # to show just the points with the same service with employer
        employee_id = request.user.employee.id
        employee = Employee.objects.get(id=employee_id)

        points = Points.objects.filter(employee=employee)

        search_counter = points.count()
        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(points, 40)  # Show 40 customers per page

        try:
            points = paginator.page(page)
        except PageNotAnInteger:
            points = paginator.page(1)
        except EmptyPage:
            points = paginator.page(paginator.num_pages)


    # Render the initial page with the full customer list
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    
    
    context = {'position': request.user.employee.position,
                'layout_path': layout_path,
                'points_with_pages': points,
                'notifications':notifications,
                'notifications_counter':notifications_counter,
                "search_counter":search_counter,
                "states":Status.objects.all(),
                'messages':messages,
                'messages_counter':messages_counter,
                'points':points

                
                }
    

    context = TemplateLayout.init(request, context)
    return render(request, 'team/points_list.html',context)


@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['team_leader']).exists() )
def point_view(request,id):
    
    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()
    messages = MessageNotify.objects.filter(employee=request.user.employee)
    messages_counter = messages.count()

    point = Points.objects.get(id = id)

    employee_id = request.user.employee.id
    employee = Employee.objects.get(id=employee_id)

    if point.employee != employee:
        point = []


    # Render the initial page with the full customer list
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    
    
    context = {'position': request.user.employee.position,
                'layout_path': layout_path,
                'notifications':notifications,
                'notifications_counter':notifications_counter,
                'messages':messages,
                'messages_counter':messages_counter,
                'point':point

                
                }
    

    context = TemplateLayout.init(request, context)
    return render(request, 'team/point.html',context)



@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['team_leader']).exists() )
def make_point_view(request):
    if request.method == 'POST':
        # Retrieve the POST data
        first_name = request.POST.get('customer-first_name')
        last_name = request.POST.get('customer-last_name')
        gender = request.POST.get('customer-gender')
        nationality_id = request.POST.get('customer-nationality')
        phone_number = request.POST.get('customer-phone_numbers')
        description = request.POST.get('customer-desc')

        # Fetch the nationality instance
        nationality = Nationality.objects.get(id=nationality_id) if nationality_id else None

        # Create and save the new Points instance
        point = Points(
            employee = request.user.employee,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            nationality=nationality,
            number=phone_number,
            description=description
        )
        point.save()

        cc = Position.objects.get(name='call center')
        employees = Employee.objects.filter(position = cc)
        for employee in employees:
            notification = InquiryNotify(
                employee = employee,
                point = point ,
                action = "new point"
            )
            notification.save()

            isnotify = IsEmployeeNotified(
                employee = employee,
                notified = False
            )
            isnotify.save()

        # Redirect or render a response after saving
        return redirect('points_list') 

        

    # selection fields

    Genders = [{'gender':"Male",'id':'male'},
                {'gender':"Female",'id':'female'}]
    
    Nationalities = Nationality.objects.all()


    types = [{'type':"House",'id':'house'},
                {'type':"Company",'id':'company'}]


    # Set the layout path even when authentication fails
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'position': request.user.employee.position,
                'layout_path': layout_path,

                'Genders':Genders,
                'Nationalities':Nationalities,

                'types':types,

                }
    
    context = TemplateLayout.init(request, context)
    return render(request, 'team/make_point.html', context)
