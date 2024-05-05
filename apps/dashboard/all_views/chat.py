from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from apps.dashboard.models import Message
from django.utils import timezone




from ..models import Inquiry, Quotation, QuotationForm, Customer, PhoneNumber, Email, Service, Booking
from apps.authentication.models import Employee, Permission, Position
from apps.dashboard.models import (EmployeeAction, Inquiry, InquiryNotify, InquiryReminder)
from apps.dashboard.models import QuotationForm, Advence, Invoice, Complain, Message, MessageNotify, IsEmployeeReadMessage, GroupMessenger, MessageGroup
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

    # Extract sources from the retrieved MessageNotify objects
    myNotifies = MessageNotify.objects.filter(employee=request.user.employee)
    myNotifies = myNotifies.filter(from_group=False)
    sources = [notify.source for notify in myNotifies]
    
    

    if search:
        employees = Employee.objects.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search))
        print('user is :',employees)

        messages = Message.objects.filter(source=request.user.employee).order_by('-created')
        inquiries_list = []
        for message in messages:
            if message.destination not in [inq['destination'] for inq in inquiries_list ] :
                inquiry = message.inquiry
                destination = message.destination
                last_content = Message.objects.filter(Q(source=request.user.employee,destination=destination) | Q(source=destination,destination=request.user.employee)).order_by('-created').first().content
                time_of_last_content = Message.objects.filter(Q(source=request.user.employee,destination=destination) | Q(source=destination,destination=request.user.employee)).order_by('-created').first().created
                formatted_time_difference = format_time_difference(time_of_last_content)
                if destination in employees:
                    if destination in sources:
                        line = {"inquiry":inquiry,'date':formatted_time_difference, 'last_content':last_content, 'destination':destination,'haveNotify':True}
                        inquiries_list.append(line)
                    else:
                        line = {"inquiry":inquiry,'date':formatted_time_difference, 'last_content':last_content, 'destination':destination,'haveNotify':False}
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
                destination = message.destination
                last_content = Message.objects.filter(Q(source=request.user.employee,destination=destination) | Q(source=destination,destination=request.user.employee)).order_by('-created').first().content
                time_of_last_content = Message.objects.filter(Q(source=request.user.employee,destination=destination) | Q(source=destination,destination=request.user.employee)).order_by('-created').first().created
                formatted_time_difference = format_time_difference(time_of_last_content)

                if destination in sources:
                    line = {"inquiry":inquiry,'date':formatted_time_difference, 'last_content':last_content, 'destination':destination,'haveNotify':True}
                    inquiries_list.append(line)
                else:
                    line = {"inquiry":inquiry,'date':formatted_time_difference, 'last_content':last_content, 'destination':destination,'haveNotify':False}
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

    employee1 = Employee.objects.get(id=Myid)  # Example: Get employee1 by id
    employee2 = Employee.objects.get(id=Otherid)  # Example: Get employee2 by id

    # delete the notification for this this two id
    try :
        the_notifications = MessageNotify.objects.filter(Q(source=employee2, employee=employee1))
        for notify in the_notifications:
                notify.delete()
                notify_info = IsEmployeeReadMessage.objects.filter(employee = request.user.employee)
                notify_info.delete()
    except :
        pass


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
            source = Employee.objects.get(id=Myid),
            from_group = False,
        )
        notification.save()

        isnotify = IsEmployeeReadMessage(
                    employee = employee,
                    notified = False,
                )
        isnotify.save()




    #messages = Message.objects.filter(inquiry=inquiry)



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


def create_group_view(request):
    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()
    messages = MessageNotify.objects.filter(employee=request.user.employee)
    messages_counter = messages.count()

    if request.method == 'POST':
        name = request.POST.get('group-name')
        members = request.POST.getlist('employees')

        print(name,members)
        newgroup = GroupMessenger(name = name)
        newgroup.save()
        for member in members:
            newgroup.members.add(member)
            newgroup.save()

        newgroup.members.add(request.user.employee)
        newgroup.save()
        
        return redirect("conversation_group_view", groupid=newgroup.id)





    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {
        'position': request.user.employee.position,
        'layout_path': layout_path,
        'notifications':notifications,
        'notifications_counter':notifications_counter,
        'messages': messages, 
        'messages_counter':messages_counter,
        'employees':Employee.objects.all(),


        }
    context = TemplateLayout.init(request, context)
    return render(request, 'chat/newgroup.html', context)



def groups_page(request):
    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()
    messages = MessageNotify.objects.filter(employee=request.user.employee)
    messages_counter = messages.count()

    # Extract sources from the retrieved MessageNotify objects
    myNotifies = MessageNotify.objects.filter(employee=request.user.employee)
    myNotifies = myNotifies.filter(from_group=True)
    grps = [notify.group for notify in myNotifies]

    gs = GroupMessenger.objects.filter(members=request.user.employee)
    groups = []
    for g in gs:

        last_message = MessageGroup.objects.filter(group=g).last()
        try:
            date = MessageGroup.objects.filter(group=g).order_by('-created').first().created
            date = format_time_difference(date)
        except:
            date = 'Make it now !'

        try:
            last_date = last_message.created
        except:
            last_date = g.created

        if g in grps:
            line = {'id':g.id,'name':g.name,'last_message':last_message,'date':date,'haveNotify':True,'last_date':last_date}
        else :
            line = {'id':g.id,'name':g.name,'last_message':last_message,'date':date,'haveNotify':False,'last_date':last_date}
        groups.append(line)

        groups = sorted(groups, key=lambda x: x['last_date'], reverse=True)


    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {
        'position': request.user.employee.position,
        'layout_path': layout_path,
        'notifications':notifications,
        'notifications_counter':notifications_counter,
        'messages': messages, 
        'messages_counter':messages_counter,
        'employees':Employee.objects.all(),
        'groups':groups,


        }
    context = TemplateLayout.init(request, context)
    return render(request, 'chat/groups_page.html', context)





def conversation_group_view(request,groupid):


    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()
    messages = MessageNotify.objects.filter(employee=request.user.employee)
    messages_counter = messages.count()

    group = GroupMessenger.objects.get(id=groupid)
    messages = MessageGroup.objects.filter(group=group).order_by('created')



    # delete the notification for this this two id
    try :
        the_notifications = MessageNotify.objects.filter(Q(group = group , employee=request.user.employee))
        for notify in the_notifications:
                notify.delete()
                notify_info = IsEmployeeReadMessage.objects.filter(employee = request.user.employee)
                notify_info.delete()
    except :
        pass



    if request.method == 'POST':
        content = request.POST.get('content')
        source = request.user.employee

        message = MessageGroup.objects.create(
                group = group,
                source = source,
                content = content
            )



        #create notification
        employees = group.members.exclude(user=request.user)
        for employee in employees:
        
            notification = MessageNotify(
                employee = employee,
                source = source,
                from_group = True,
                group = group,
            )
            notification.save()

            isnotify = IsEmployeeReadMessage(
                        employee = employee,
                        notified = False,
                    )
            isnotify.save()





    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {
        'position': request.user.employee.position,
        'layout_path': layout_path,
        'notifications':notifications,
        'notifications_counter':notifications_counter,
        'messages': messages, 
        'messages_counter':messages_counter,
        'employees':Employee.objects.all(),
        'group':group,


        }
    context = TemplateLayout.init(request, context)
    return render(request, 'chat/group_conversation.html', context)
