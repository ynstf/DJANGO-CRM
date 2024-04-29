from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from apps.dashboard.models import Message
from django.utils import timezone




from ..models import Inquiry, Quotation, QuotationForm, Customer, PhoneNumber, Email, Service, Booking
from apps.authentication.models import Employee, Permission, Position
from apps.dashboard.models import (EmployeeAction, Inquiry, InquiryNotify, InquiryReminder,
    InquiryStatus, IsEmployeeNotified, Language, Nationality, Quotation, Source, Status,
    SuperProvider)
from apps.dashboard.models import QuotationForm, Advence, Invoice, Complain, Message, MessageNotify, IsEmployeeReadMessage
from django.db.models import Q


def format_time_difference(created_time):
    current_time = timezone.now()  # Get the current time in UTC
    time_difference = current_time - created_time

    days = time_difference.days
    seconds = time_difference.total_seconds()

    if days > 0:
        return f"{days} {'day' if days == 1 else 'days'} ago"
    elif seconds >= 3600:
        hours = int(seconds // 3600)
        return f"{hours} {'hour' if hours == 1 else 'hours'} ago"
    elif seconds >= 60:
        minutes = int(seconds // 60)
        return f"{minutes} {'minute' if minutes == 1 else 'minutes'} ago"
    else:
        return "Just now"

@login_required(login_url='/')
def chat_page(request):
    title = "Chat"
    search = request.GET.get("search")
    if search:
        employees = Employee.objects.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search))
        print('user is :',employees)


        messages = Message.objects.filter(source=request.user.employee).order_by('-created')
        inquiries_list = []
        for message in messages:
            if message.inquiry not in [inq['inquiry'] for inq in inquiries_list ] :
                inquiry = message.inquiry
                last_content = message.content
                destination = message.destination
                formatted_time_difference = format_time_difference(message.created)
                if destination in employees:
                    line = {"inquiry":inquiry,'date':formatted_time_difference, 'last_content':last_content, 'destination':destination}
                    inquiries_list.append(line)

        dists = [msg['destination'] for msg in inquiries_list]
        distinations=[]

        for employee in employees:
            if employee not in dists and employee!=request.user.employee:
                distinations.append(employee)

    else:
        messages = Message.objects.filter(source=request.user.employee).order_by('-created')
        inquiries_list = []
        for message in messages:
            if message.inquiry not in [inq['inquiry'] for inq in inquiries_list ] :
                inquiry = message.inquiry
                last_content = message.content
                destination = message.destination
                formatted_time_difference = format_time_difference(message.created)
                line = {"inquiry":inquiry,'date':formatted_time_difference, 'last_content':last_content, 'destination':destination}
                inquiries_list.append(line)

        dists = [msg['destination'] for msg in inquiries_list]
        distinations=[]
        employees = Employee.objects.all()
        for employee in employees:
            if employee not in dists and employee!=request.user.employee:
                distinations.append(employee)


    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'title':title,
                'position': request.user.employee.position,
                'layout_path': layout_path,
                'messages': inquiries_list,
                'distinations': distinations,


                }
    context = TemplateLayout.init(request, context)
    return render(request, 'chat/chat_page.html', context)


def conversation_view(request, Myid, Otherid):


    """# delete the notification for this inquiry id
    try :
        the_notifications = MessageNotify.objects.filter(inquiry=inquiry)
        for notify in the_notifications:
            if notify.employee.user == request.user:
                notify.delete()
                notify_info = IsEmployeeReadMessage.objects.filter(employee = request.user.employee)
                notify_info.delete()
    except :
        pass"""


    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()
    messages = MessageNotify.objects.filter(employee=request.user.employee)
    messages_counter = messages.count()
    

    

    if request.method == 'POST':
        content = request.POST.get('content')
        source = request.user.employee
        employees = Employee.objects.get(id=Otherid)

        message = Message.objects.create(
                source = source,
                destination = employees ,
                content = content
            )


        #create notification
        employee = Employee.objects.get(id=Otherid)
        notification = MessageNotify(
            employee = employee,

        )
        notification.save()

        isnotify = IsEmployeeReadMessage(
                    employee = employee,
                    notified = False,
                )
        isnotify.save()




    #messages = Message.objects.filter(inquiry=inquiry)

    employee1 = Employee.objects.get(id=Myid)  # Example: Get employee1 by id
    employee2 = Employee.objects.get(id=Otherid)  # Example: Get employee2 by id

    # Retrieve all messages where source=employee1 and destination=employee2 OR source=employee2 and destination=employee1
    messages = Message.objects.filter(Q(source=employee1, destination=employee2) | Q(source=employee2, destination=employee1)).order_by('created')

    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {
        'position': request.user.employee.position,
        'layout_path': layout_path,
        'notifications':notifications,
        'notifications_counter':notifications_counter,
        'messages': messages, 
        'messages_counter':messages_counter,
        'destination':Employee.objects.get(id=Otherid),

        }
    context = TemplateLayout.init(request, context)
    return render(request, 'chat/conversation.html', context)
