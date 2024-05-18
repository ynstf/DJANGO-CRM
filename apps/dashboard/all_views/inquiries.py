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
from ..models import Inquiry, Quotation, QuotationForm, Customer, PhoneNumber, Email, Service, Booking
from apps.authentication.models import Employee, Permission, Position
from apps.dashboard.models import (EmployeeAction, Inquiry, InquiryNotify, InquiryReminder,
    InquiryStatus, IsEmployeeNotified, Language, Nationality, Quotation, Source, Status,
    SuperProvider)
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.urls import reverse
from urllib.parse import quote
from datetime import timedelta
from apps.dashboard.models import QuotationForm, Advence, Invoice, Complain, Message, MessageNotify, IsEmployeeReadMessage
import cloudinary
import cloudinary.uploader
import json
from datetime import datetime

################# permissions ############
"""
inquiry list
inquiry info
make quotation
edit quotation
extract quotations
"""
def map(request):
    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()
    messages = MessageNotify.objects.filter(employee=request.user.employee)
    messages_counter = messages.count()


    status = request.GET.get('status')
    start = request.GET.get('start')
    finish = request.GET.get('finish')
    service = request.GET.get('service')
    sp = request.GET.get('sp')


    inquiries = Inquiry.objects.all()

    if status :
        st = Status.objects.get(id=status)
        inquiries = Inquiry.objects.filter(inquirystatus__status=st)
        status=int(status)

    if start or finish :
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        finish_date = datetime.strptime(finish, '%Y-%m-%d').date()
        inquiries = inquiries.filter(date_inq__range=[start_date, finish_date])
    
    if service :
        inquiries = inquiries.filter(services=service)
        service = int(service)
    
    if sp :
        inquiries = inquiries.filter(sp=sp)
        sp = int(sp)
    
    
    coord = []
    for i in inquiries:
        data = i.address.location.split(',')
        if len(data)==2:
            coord.append(data)


    search_str = {
        'status':status,
        'start':start,
        'finish':finish,
        'service': service,
        'sp' : sp,
    }

    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'position': request.user.employee.position,
            'layout_path': layout_path,
            'notifications':notifications,
            'notifications_counter':notifications_counter,
            'messages':messages,
            'messages_counter':messages_counter,

            'services':Service.objects.all(),
            'states':Status.objects.all(),
            'service_providers':SuperProvider.objects.all(),
            'coord':json.dumps(coord),
            'search_str':search_str,

            }
    context = TemplateLayout.init(request, context)

    return render(request,"map.html",context)


################# inquiries ###################


def make_inq_cancel(request,inq_id):
    if request.method == 'POST':
        canceling_causes = request.POST.get('canceling_causes')

    cancel = Status.objects.get(name = "cancel")
    inquiry = Inquiry.objects.get(id = inq_id)
    inq_state = InquiryStatus.objects.get(inquiry = inquiry)
    inq_state.status = cancel
    try:
        inq_state.canceling_causes = canceling_causes
    except:
        inq_state.canceling_causes = "None"
    inq_state.save()

    #create action
    action = EmployeeAction(
        from_employee=request.user.employee,
        inquiry = inquiry,
        status = InquiryStatus.objects.get(inquiry = inquiry).status
    )
    action.save()

    return redirect('inquiries_list')

def make_inq_new(request,inq_id):
    new = Status.objects.get(name = "new")
    inquiry = Inquiry.objects.get(id = inq_id)
    inq_state = InquiryStatus.objects.get(inquiry = inquiry)
    inq_state.status = new
    inq_state.save()

    #create action
    action = EmployeeAction(
        from_employee=request.user.employee,
        inquiry = inquiry,
        status = InquiryStatus.objects.get(inquiry = inquiry).status
    )
    action.save()

    return redirect('inquiries_list')

def make_inq_connecting(request,inq_id):
    connecting = Status.objects.get(name = "connecting")
    inquiry = Inquiry.objects.get(id = inq_id)
    inq_state = InquiryStatus.objects.get(inquiry = inquiry)
    inq_state.status = connecting
    inq_state.save()


    #create action
    action = EmployeeAction(
        from_employee=request.user.employee,
        inquiry = inquiry,
        status = InquiryStatus.objects.get(inquiry = inquiry).status
    )
    action.save()

    cc = Position.objects.get(name="call center")
    all_employees = Employee.objects.filter(position=cc)

    #create notification
    for employee in all_employees:
        notification = InquiryNotify(
            employee = employee,
            inquiry = inquiry,
            service = inquiry.services,
            action = "connecting"
        )
        notification.save()
        isnotify = IsEmployeeNotified(
            employee = employee,
            notified = False
        )
        isnotify.save()
    return redirect('inquiries_list')

def make_inq_sendQ(request,inq_id):
    sendQ  = Status.objects.get(name = "send Q or B")
    inquiry = Inquiry.objects.get(id = inq_id)
    inq_state = InquiryStatus.objects.get(inquiry = inquiry)
    inq_state.status = sendQ
    inq_state.save()

    #create action
    action = EmployeeAction(
        from_employee=request.user.employee,
        inquiry = inquiry,
        status = InquiryStatus.objects.get(inquiry = inquiry).status
    )
    action.save()

    #create notification
    cc = Position.objects.get(name="call center")
    all_employees = Employee.objects.filter(position=cc)
    for employee in all_employees:
        notification = InquiryNotify(
            employee = employee,
            inquiry = inquiry,
            service = inquiry.services,
            action = "send quotation"
        )
        notification.save()
        isnotify = IsEmployeeNotified(
            employee = employee,
            notified = False
        )
        isnotify.save()
    return redirect('inquiries_list')

def make_inq_pending(request,inq_id):
    pending  = Status.objects.get(name = "pending")
    inquiry = Inquiry.objects.get(id = inq_id)
    inq_state = InquiryStatus.objects.get(inquiry = inquiry)
    inq_state.status = pending
    inq_state.save()

    #create action
    action = EmployeeAction(
        from_employee=request.user.employee,
        inquiry = inquiry,
        status = InquiryStatus.objects.get(inquiry = inquiry).status
    )
    action.save()


    #create notification
    all_employees = Employee.objects.filter(sp=inquiry.sp)
    for employee in all_employees:
        notification = InquiryNotify(
            employee = employee,
            inquiry = inquiry,
            service = inquiry.services,
            action = "pending"
        )
        notification.save()
        isnotify = IsEmployeeNotified(
            employee = employee,
            notified = False
        )
        isnotify.save()

    return redirect('inquiries_list')

def make_inq_complain(request,inq_id):
    complain  = Status.objects.get(name = "complain")
    inquiry = Inquiry.objects.get(id = inq_id)
    inq_state = InquiryStatus.objects.get(inquiry = inquiry)
    inq_state.status = complain
    inq_state.save()

    #create action
    action = EmployeeAction(
        from_employee=request.user.employee,
        inquiry = inquiry,
        status = InquiryStatus.objects.get(inquiry = inquiry).status
    )
    action.save()


    #create notification
    all_employees = Employee.objects.filter(sp=inquiry.sp)
    for employee in all_employees:
        notification = InquiryNotify(
            employee = employee,
            inquiry = inquiry,
            service = inquiry.services,
            action = "complain"
        )
        notification.save()
        isnotify = IsEmployeeNotified(
            employee = employee,
            notified = False
        )
        isnotify.save()

    return redirect('inquiries_list')

def make_inq_done(request,inq_id):
    done  = Status.objects.get(name = "done")
    inquiry = Inquiry.objects.get(id = inq_id)
    inq_state = InquiryStatus.objects.get(inquiry = inquiry)
    inq_state.status = done
    inq_state.save()

    #create action
    action = EmployeeAction(
        from_employee=request.user.employee,
        inquiry = inquiry,
        status = InquiryStatus.objects.get(inquiry = inquiry).status
    )
    action.save()


    #create notification
    all_employees = Employee.objects.filter(sp=inquiry.sp)
    for employee in all_employees:
        notification = InquiryNotify(
            employee = employee,
            inquiry = inquiry,
            service = inquiry.services,
            action = "done"
        )
        notification.save()
        isnotify = IsEmployeeNotified(
            employee = employee,
            notified = False
        )
        isnotify.save()

    return redirect('inquiries_list')


def get_messages(request):

    messages = MessageNotify.objects.filter(employee=request.user.employee)
    messages_counter = messages.count()
    messages_data = [{'message': str(message)} for message in messages]
    return JsonResponse({'messages': messages_data, 'messages_counter': messages_counter}, safe=False)

def get_message_state_view(request):
    print(request.user.employee)
    
    try:
        notify_info = IsEmployeeReadMessage.objects.get(employee = request.user.employee)
        print(notify_info.notified)
        return JsonResponse({'notify_info': notify_info.notified}, safe=False)
    except:
        return JsonResponse({}, safe=False)

def make_employee_readmessage_view(request):
    notify_info = IsEmployeeReadMessage.objects.get(employee = request.user.employee)
    notify_info.notified = True
    notify_info.save()
    print(notify_info.notified)
    return JsonResponse({'resp': True})

@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['call_center','provider', 'admin', 'team_leader']).exists() or (Permission.objects.get(name="inquiry info") in u.employee.permissions.all()) )
def messages_list_view(request):
    messages = MessageNotify.objects.filter(employee=request.user.employee)
    messages_counter = messages.count()

    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'position': request.user.employee.position,
            'layout_path': layout_path,
            'messages':messages,
            'messages_counter':messages_counter,

            }
    context = TemplateLayout.init(request, context)
    return render(request, "inquiry/messages.html", context)


def get_notifications(request):
    current_date = timezone.now().date()
    try:
        reminders = InquiryReminder.objects.filter(employee=request.user.employee, schedule__lte=current_date)
        for reminder in reminders:
            notification = InquiryNotify(
                employee = reminder.employee,
                inquiry = reminder.inquiry,
                service = reminder.service,
                action = "reminder"
            )
            notification.save()
            reminder.delete()
    except:
        pass



    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()
    notifications_data = [{'message': str(notification)} for notification in notifications]
    return JsonResponse({'notifications': notifications_data, 'notifications_counter': notifications_counter}, safe=False)

def get_notify_state_view(request):
    print(request.user.employee)
    
    try:
        notify_info = IsEmployeeNotified.objects.get(employee = request.user.employee)
        print(notify_info.notified)
        return JsonResponse({'notify_info': notify_info.notified}, safe=False)
    except:
        return JsonResponse({}, safe=False)

def make_employee_notified_view(request):
    notify_info = IsEmployeeNotified.objects.get(employee = request.user.employee)
    notify_info.notified = True
    notify_info.save()
    print(notify_info.notified)
    return JsonResponse({'resp': True})

@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['call_center','provider', 'admin', 'team_leader']).exists() or (Permission.objects.get(name="inquiry info") in u.employee.permissions.all()) )
def notifications_view(request):
    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()
    messages = MessageNotify.objects.filter(employee=request.user.employee)
    messages_counter = messages.count()

    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'position': request.user.employee.position,
            'layout_path': layout_path,
            'notifications':notifications,
            'notifications_counter':notifications_counter,
            'messages':messages,
            'messages_counter':messages_counter,

            }
    context = TemplateLayout.init(request, context)
    return render(request, "inquiry/notifications.html", context)


@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['call_center','provider', 'admin','team_leader']).exists() or (Permission.objects.get(name="inquiry list") in u.employee.permissions.all()) )
def inquiries_list_view(request):
    inquiries = Inquiry.objects.all()

    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()
    messages = MessageNotify.objects.filter(employee=request.user.employee)
    messages_counter = messages.count()



    # Handle search form submission
    if request.method == 'GET':
        # Get the name entered in the query parameter
        name_query = request.GET.get('name')
        id_query = request.GET.get('id')

        service_query = request.GET.get('service')

        #number_query = request.GET.get('number')
        language_query = request.GET.get('language')
        nationality_query = request.GET.get('nationality')
        source_query = request.GET.get('source')
        status_query = request.GET.get('status')
        #date_query = request.GET.get('date')
        add_name_query = request.GET.get('add_name')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        reminder = request.GET.get('reminder')


        search_fields = []

        if name_query:
            search_fields.append({'name':'name',
                                'value':name_query})
            inquiries = inquiries.filter(customer__first_name__icontains=name_query)
        
        if id_query:
            search_fields.append({'name':'id',
                                'value':id_query})
            inquiries = inquiries.filter(id=id_query)

        if start_date and end_date:
            search_fields.append({'name': 'date', 'start_date': start_date, "end_date":end_date })
            inquiries = inquiries.filter(date_inq__range=[start_date, end_date])

        if add_name_query:
            search_fields.append({'name':'add_name',
                                'value':add_name_query})
            inquiries = inquiries.filter(address__address_name__icontains=add_name_query)
        
        if source_query:
            search_fields.append({'name':'source',
                                'value':source_query})
            id = Source.objects.get(name=source_query)
            inquiries = inquiries.filter(source=id)

        if status_query:
            search_fields.append({'name':'status',
                                'value':status_query})
            id = Status.objects.get(name=status_query)

            inquiries = inquiries.filter(inquirystatus__status=id)

        if language_query:
            search_fields.append({'name':'language',
                                'value':language_query})
            id = Language.objects.get(name=language_query)
            inquiries = inquiries.filter(customer__language=id)

        if nationality_query:
            search_fields.append({'name':'nationality',
                                'value':nationality_query})
            id = Nationality.objects.get(name=nationality_query)
            inquiries = inquiries.filter(customer__nationality=id)

        # Get today's date
        today = timezone.now().date()

        if reminder:

            if reminder == '1':
                # Reminder today or tomorrow
                end_date = today + timedelta(days=1)
                reminder = 'Reminder today or tomorrow'
            elif reminder == '2':
                # Reminder next 1 month
                end_date = today + timedelta(days=30)
                reminder = "Reminder next 1 month"
            elif reminder == '3':
                # Reminder next 3 months
                end_date = today + timedelta(days=90)
                reminder = "Reminder next 3 months"
            elif reminder == '4':
                # Reminder next 6 months
                end_date = today + timedelta(days=180)
                reminder = "Reminder next 6 months"
            elif reminder == '5':
                # Reminder next 12 months
                end_date = today + timedelta(days=365)
                reminder = "Reminder next 12 months"

            search_fields.append({'name':'reminder',
                                'value':reminder})

            # Filter Inquiry objects based on the related InquiryReminder objects
            inquiries = Inquiry.objects.filter(inquiryreminder__schedule__range=[today, end_date])
            

        

        # to show just the inquiries with the same service with employer
        employee_id = request.user.employee.id
        employee = Employee.objects.get(id=employee_id)
        try:
            #srvc_id = employee.sp_service.id
            #inquiries = inquiries.filter(services=srvc_id)
            sp_id = employee.sp.id
            inquiries = inquiries.filter(sp=sp_id)
        except:
            pass


        search_counter = inquiries.count()

        try :
            search_number = request.user.employee.sp.search_number
            #order inquiries by last updated
            inquiries = inquiries.order_by('-inquirystatus__update')[:search_number]
        except:
            inquiries = inquiries.order_by('-inquirystatus__update')
        search_counter = inquiries.count()



        sort_fields = request.GET.getlist('sort_field')
        sortSence= []
        for d in sort_fields :
            sortSence.append(request.GET.get(d))

        merged_list = list(zip(sort_fields, sortSence))

        for column in merged_list:
            if column[0] == "inq_id":
                if column[1] == 'asc':
                    inquiries = inquiries.order_by('id')
                else:
                    inquiries = inquiries.order_by('-' + 'id')

            if column[0] == "customer_id":
                if column[1] == 'asc':
                    inquiries = inquiries.order_by('customer__id')
                else:
                    inquiries = inquiries.order_by('-' + 'customer__id')

            if column[0] == "creation":
                if column[1] == 'asc':
                    inquiries = inquiries.order_by('date_inq')
                else:
                    inquiries = inquiries.order_by('-' + 'date_inq')

            if column[0] == "update":
                if column[1] == 'asc':
                    inquiries = inquiries.order_by('inquirystatus__update')
                else:
                    inquiries = inquiries.order_by('-' + 'inquirystatus__update')

            if column[0] == "customer":
                if column[1] == 'asc':
                    inquiries = inquiries.order_by('customer__first_name')
                    print(inquiries)
                else:
                    inquiries = inquiries.order_by('-' + 'customer__first_name')

            if column[0] == "service_sort":
                if column[1] == 'asc':
                    inquiries = inquiries.order_by('services')
                    print(inquiries)
                else:
                    inquiries = inquiries.order_by('-' + 'services')

            if column[0] == "source_sort":
                if column[1] == 'asc':
                    inquiries = inquiries.order_by('source')
                    print(inquiries)
                else:
                    inquiries = inquiries.order_by('-' + 'source')

            if column[0] == "state_sort":
                if column[1] == 'asc':
                    inquiries = inquiries.order_by('inquirystatus__status')
                    print(inquiries)
                else:
                    inquiries = inquiries.order_by('-' + 'inquirystatus__status')

            if column[0] == "sp_sort":
                if column[1] == 'asc':
                    inquiries = inquiries.order_by('sp')
                    print(inquiries)
                else:
                    inquiries = inquiries.order_by('-' + 'sp')




        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(inquiries, 40)  # Show 40 customers per page

        try:
            inquiries = paginator.page(page)
        except PageNotAnInteger:
            inquiries = paginator.page(1)
        except EmptyPage:
            inquiries = paginator.page(paginator.num_pages)

    inquiry = []
    for i in inquiries:
        try:
            advence = Advence.objects.get(inquiry=i)
        except :
            advence = 0

        try:
            # Assuming 'i' is the specific inquiry instance
            quotations = Quotation.objects.filter(inquiry=i)
            totale = 0
            for q in quotations:
                totale = totale + float(q.total)
        except:
            totale = 0
            

        try:
            inquiry.append({'info':i,
                            'state':InquiryStatus.objects.get(inquiry=i),
                            'advence' : advence,
                            'totale':totale,
                            'action':EmployeeAction.objects.filter(inquiry=i).last()
                        })
        except:
            inquiry.append({'info':i,
                        })

    try:
        cols = request.user.employee.sp.columns.split("*,*")
    except:
        cols = "all"

    # Render the initial page with the full customer list
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    
    
    context = {'position': request.user.employee.position,
                'layout_path': layout_path,
                'inquiries_with_pages': inquiries,
                'inquiries': inquiry,
                'notifications':notifications,
                'notifications_counter':notifications_counter,
                "search_counter":search_counter,
                "states":Status.objects.all(),
                'messages':messages,
                'messages_counter':messages_counter,

                'search_fields':search_fields,

                "data":merged_list,
                "cols":cols,
                
                }
    

    context = TemplateLayout.init(request, context)
    return render(request, 'inquiry/inquiries_list.html',context)


def add_advence_view(request, id):
    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()
    messages = MessageNotify.objects.filter(employee=request.user.employee)
    messages_counter = messages.count()

    inquiry = Inquiry.objects.get(id=id)
    inquiry_state = InquiryStatus.objects.get(inquiry=inquiry)
    customer = inquiry.customer
    if request.method == 'POST':
        advence_price = request.POST.get('advence_price')
        print(advence_price)
        try :
            advence = Advence.objects.get(inquiry=inquiry)
            print(advence)
            print("11111111111111")
            advence.price = float(advence.price) + float(advence_price)
            advence.save()
        except :
            print("222222222222222")
            advence = Advence.objects.create(inquiry=inquiry)
            advence.price = advence_price
            advence.save()

    return redirect('inquiries_list')


@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['call_center','provider', 'admin', 'team_leader']).exists() or (Permission.objects.get(name="inquiry info") in u.employee.permissions.all()) )
def inquiry_info_view(request, id):

    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()
    messages = MessageNotify.objects.filter(employee=request.user.employee)
    messages_counter = messages.count()

    inquiry = Inquiry.objects.get(id=id)
    inquiry_state = InquiryStatus.objects.get(inquiry=inquiry)
    customer = inquiry.customer


    # upload images 
    if request.method == 'POST':
        try:
            imgs = request.FILES.getlist('images')
            print(imgs)
            # Upload images to Cloudinary
            image_urls = []
            for img in imgs:
                cloudinary_response = cloudinary.uploader.upload(img)
                image_urls.append(cloudinary_response['secure_url'])
            # Get the public URL(s) of the uploaded image(s)
            try:
                urls = inquiry.cloudinary_urls.split(',**,')
            except:
                urls = []
            image_urls+=urls
            # Save the URL(s) to the model
            inquiry.cloudinary_urls = ',**,'.join(image_urls)
            inquiry.save()
        except:
            pass

    try:
        images = inquiry.cloudinary_urls.split(',**,')
        print(images)
    except:
        images = "" 

    # delete the notification for this inquiry id
    try :
        the_notifications = InquiryNotify.objects.filter(inquiry=inquiry)
        for notify in the_notifications:
            if notify.employee.user == request.user:
                notify.delete()
                notify_info = IsEmployeeNotified.objects.filter(employee = request.user.employee)
                notify_info.delete()
    except :
        pass

    # Retrieve the Service instance
    service_instance = inquiry.services
    # Convert the comma-separated string back to a list
    try:
        columns_list = service_instance.columns.split(',')
        print(columns_list)
    except:
        columns_list = []
        pass

    inquiry_data = []
    quotations = Quotation.objects.filter(inquiry=Inquiry.objects.get(id=id))
    for quotation in quotations:
        line = quotation.data.split(',*,')
        print(line)
        inquiry_data.append(line)
    
    try:
        booking_detail = Booking.objects.get(inquiry=inquiry).details 
        booking_number = Booking.objects.get(inquiry=inquiry).booking_number
        booking_date = Booking.objects.get(inquiry=inquiry).booking_date
    except:
        booking_detail = None
        booking_number = None
        booking_date = None

    try:
        schedule_date = InquiryReminder.objects.get(inquiry=inquiry).schedule
    except:
        schedule_date = None


    try:
        # Assuming you want to include a predefined message
        phone_number = customer.whatsapp_set.all().first().whatsapp
    except :
        phone_number = ""
    
    message = "Your Quotations ready, check the link"
    # Replace 'https://example.com/path/to/your/document.pdf' with the actual URL to your hosted PDF document
    pdf_url = reverse('generate_pdf', args=[id])
    absolute_pdf_url = request.build_absolute_uri(pdf_url)
    # Construct the WhatsApp link with the PDF document link
    whatsapp_link = f'https://api.whatsapp.com/send?phone={phone_number}&text={quote(message)}%0A{quote(str(absolute_pdf_url))}'

    message = "Your Invoice ready, check the link"
    pdf_url = reverse('generate_invoice', args=[id])
    absolute_pdf_url = request.build_absolute_uri(pdf_url)
    whatsapp_link_invoice = f'https://api.whatsapp.com/send?phone={phone_number}&text={quote(message)}%0A{quote(str(absolute_pdf_url))}'

    
    connect_with_customer_whatsapp_link = f'https://api.whatsapp.com/send?phone={phone_number.replace("+","")}'


    print(schedule_date)
    print(booking_number)
    print('haaaaaaaaaaaaaaaaaaaaaaa',Inquiry.objects.get(id=id).handler.all())

    try:
        complain = Complain.objects.get(inquiry=inquiry)
    except:
        complain = None


    status = []
    call_center_actions = ['pending','new','cancel','done','complain','underproccess']
    service_provider_actions = ['connecting','send Q or B','underproccess','new']
    for state in Status.objects.all():
        if request.user.employee.position.name == "call center" and state.name in call_center_actions :
            status.append(state)
        elif request.user.employee.position.name == "super provider" and state.name in service_provider_actions :
            status.append(state)


    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'position': request.user.employee.position,
            'layout_path': layout_path,
            'notifications':notifications,
            'notifications_counter':notifications_counter,
            'customer': customer,
            'inquiry': inquiry,
            'inquiry_state':inquiry_state,
            'columns_list':columns_list,
            'data':inquiry_data,
            'booking_detail':booking_detail,
            'booking_number':booking_number,
            'booking_date':booking_date,
            'schedule_date':schedule_date,
            'complain':complain,
            'messages':messages,
            'messages_counter':messages_counter,


            'quotations': Quotation.objects.filter(inquiry=Inquiry.objects.get(id=id)),
            'permissions_list':[p.name for p in request.user.employee.permissions.all()],
            'whatsapp_link':whatsapp_link,
            'whatsapp_link_invoice':whatsapp_link_invoice,
            'connect_with_customer_whatsapp_link':connect_with_customer_whatsapp_link,
            'canceling_cause': inquiry_state.canceling_causes,
            'images': images,

            'status':status,
            'handlers':inquiry.handler.all(),

            }
    context = TemplateLayout.init(request, context)
    return render(request, "inquiry/inquiries_info.html", context)


@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['provider', 'admin']).exists() or (Permission.objects.get(name="make quotation") in u.employee.permissions.all()) )
def make_quotation_view(request, id):
    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()
    messages = MessageNotify.objects.filter(employee=request.user.employee)
    messages_counter = messages.count()



    if request.method == 'POST':

        quotation_service = request.POST.get('quotation-service')
        sp = request.POST.get('quotation-sp')
        quotation_date = request.POST.get('quotation-date')


        inquiry = Inquiry.objects.get(id=id)
        customer_id = inquiry.customer.id
        customer = Customer.objects.get(id=customer_id)
        employee_id = request.user.employee.id
        employee = Employee.objects.get(id=employee_id)

        # Retrieve the Service instance
        service_instance = inquiry.services
        # Convert the comma-separated string back to a list
        columns_list = service_instance.columns.split(',')


        srv_id = service_instance.id
        quotation_service = Service.objects.get(id=srv_id)

        lent = request.POST.getlist('quotation-price')
        superprovider = SuperProvider.objects.get(id=sp)

        original_string = superprovider.reference
        # Find the index of the first digit
        try:
            index_of_first_digit = next((index for index, char in enumerate(original_string) if char.isdigit()), None)
            # Split the string into two parts based on the index of the first digit
            prefix = original_string[:index_of_first_digit]
            suffix = original_string[index_of_first_digit:]
            new_invoice_ref = f'{prefix}{int(suffix)+1}'
            superprovider.reference = new_invoice_ref
            superprovider.save()
        except:
            pass

        for i in range(len(lent)):
            data = []
            for field in columns_list:
                details = request.POST.getlist(f'quotation-{field}')[i]
                data.append(details)
            total = float(data[-1])*float(data[-2])
            columns_str = ",*,".join(data)
            print(columns_str)
            
            superprovider = SuperProvider.objects.get(id=sp)
            quotation = Quotation(
                employee=employee,
                customer=customer,
                inquiry=inquiry,
                quotation_service=quotation_service,
                quotation_sp=superprovider,
                invoice_counter=superprovider.reference,
                quotation_date=quotation_date,
                data = columns_str,
                total=total
            )
            quotation.save()

            print()
        
        return redirect('make_inq_sendQ', inq_id=id)




    inquiry = Inquiry.objects.get(id=id)
    # Retrieve the Service instance
    service_instance = inquiry.services
    # Convert the comma-separated string back to a list
    columns_list = service_instance.columns.split(',')

    sp = request.user.employee.sp
    services = sp.service.all()

    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'position': request.user.employee.position,
            'layout_path': layout_path,
            'notifications':notifications,
            'notifications_counter':notifications_counter,
            'customer': Inquiry.objects.get(id=id).customer,
            'inquiry': Inquiry.objects.get(id=id),
            'services':services,
            'sp':sp,
            'columns_list':columns_list,
            'messages':messages,
            'messages_counter':messages_counter,
            }
    context = TemplateLayout.init(request, context)
    return render(request, "inquiry/make_quotation.html", context)


@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['provider', 'admin']).exists() or (Permission.objects.get(name="edit quotation") in u.employee.permissions.all()) )
def edit_quotation_view(request,id):
    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()
    messages = MessageNotify.objects.filter(employee=request.user.employee)
    messages_counter = messages.count()
    inquiry = Inquiry.objects.get(id = id)

    quotations = Quotation.objects.filter(inquiry=inquiry)

    if request.method == 'POST':
        quotation_service = request.POST.get('quotation-service')
        quotation_date = request.POST.get('quotation-date')
        details = request.POST.getlist('quotation-detail')
        prices = request.POST.getlist('quotation-price')
        quantities = request.POST.getlist('quotation-quantity')


        inquiry = Inquiry.objects.get(id=id)
        customer_id = inquiry.customer.id
        customer = Customer.objects.get(id=customer_id)
        employee_id = request.user.employee.id
        employee = Employee.objects.get(id=employee_id)

        print(employee,inquiry,customer,quotation_service,quotation_date,details,prices,quantities)
        
        srv_id = quotation_service
        quotation_service = Service.objects.get(id=srv_id)

        #delete old values
        quots = Quotation.objects.filter(inquiry=inquiry)
        quots.delete()
        #save the new values
        for i in range(len(prices)):
            quotation = Quotation(
                employee=employee,
                customer=customer,
                inquiry=inquiry,
                quotation_service=quotation_service,
                quotation_date=quotation_date,
                detail=details[i],
                price=prices[i],
                quantity=quantities[i],
                total=float(prices[i])*float(quantities[i])
            )
            quotation.save()

        return redirect('inquiry/inquiry_info', id=id)

    
    date=quotations[0].quotation_date
    service=quotations[0].quotation_service
    # Render the initial page with the full customer list
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})

    context = {'position': request.user.employee.position,
                'layout_path': layout_path,
                'notifications':notifications,
                'notifications_counter':notifications_counter,
                'inquiry': Inquiry.objects.get(id=id),
                'date':date,
                'service' : service,
                'quotations':quotations,
                'services':Service.objects.all(),
                'messages':messages,
                'messages_counter':messages_counter,

                }
    
    context = TemplateLayout.init(request, context)
    return render(request, 'inquiry/edit_quotation.html',context)

@login_required(login_url='/')
def edit_inquiry(request,id):
    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()
    messages = MessageNotify.objects.filter(employee=request.user.employee)
    messages_counter = messages.count()
    inquiry = Inquiry.objects.get(id = id)

    if request.method == 'POST':
        inq_source = request.POST.get('customer-source')
        inq_service = request.POST.get('inquiry-services')
        team_leader = request.POST.get('inquiry-team_leader')
        inq_employees = request.POST.get('inquiry-employees')
        sp = request.POST.get('inquiry-superprovider')
        inq_desc = request.POST.get('inquiry-description')

        srv = Service.objects.get(number=inq_service)
        src = Source.objects.get(id=inq_source)
        tl = Employee.objects.get(id=team_leader)
        sup = SuperProvider.objects.get(id=sp)
        owner = Employee.objects.get(id=inq_employees)
        desc = inq_desc
        print("service:" ,srv)
        print("source :",src)
        print("team :",tl)
        print("sp: ",sup)
        print("desc:",desc)
        print("owner",owner)

        inquiry.services = srv
        inquiry.source = src
        inquiry.sp = sup
        inquiry.owner = owner
        inquiry.description = desc
        inquiry.team_leader = tl

        inquiry.save()

        return redirect("inquiry_info",id=id)



    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'position': request.user.employee.position,
                'layout_path': layout_path,
                'notifications':notifications,
                'notifications_counter':notifications_counter,
                'inquiry': Inquiry.objects.get(id=id),


                'services':Service.objects.all(),
                'messages':messages,
                'messages_counter':messages_counter,
                'all_sp':SuperProvider.objects.all(),
                'Sources':Source.objects.all(),
                'team_leaders':Employee.objects.filter(position=Position.objects.get(name='team leader')),


                }
    
    context = TemplateLayout.init(request, context)
    return render(request, 'inquiry/edit_inquiry.html',context)


def generate_pdf_view(request, id):
    # Retrieve the inquiry and associated quotations
    inquiry = Inquiry.objects.get(id=id)
    quotations = Quotation.objects.filter(inquiry=inquiry)
    customer = Customer.objects.get(id=inquiry.customer.id)
    phone = PhoneNumber.objects.filter(customer=customer)[0]
    email = Email.objects.filter(customer=customer)[0]
    address = inquiry.address.address_name

    total = 0
    for quotation in quotations:
        total += float(quotation.total)


    date=quotations[0].quotation_date
    sp_quot=quotations[0].quotation_sp
    try:
        sp = QuotationForm.objects.get(title = 'Quotation1')
    except:
        sp = ''

    form = QuotationForm.objects.all().first()
    # Create a PDF template using Django template
    template_path = 'pdf_template.html'  # Create a template for your PDF
    template = get_template(template_path)


    # Retrieve the Service instance
    service_instance = inquiry.services
    # Convert the comma-separated string back to a list
    columns_list = service_instance.columns.split(',')
    columns_list.append('Total')

    data = []
    for quotation in quotations:
        datas = quotation.data.split(',*,')
        datas.append(quotation.total)
        data.append(datas)
    


    context = {'inquiry': inquiry,
                'quotations': quotations,
                'date':date,
                'service':sp_quot,
                'phone':phone,
                'address':address,
                'email':email,
                'total':total,
                'form':form,
                'columns_list':columns_list,
                'data':data,
                'sp':sp,

                }
    html_content = template.render(context)

    # Create a PDF file using ReportLab
    pdf_file = io.BytesIO()
    pisa.CreatePDF(html_content, dest=pdf_file)

    # Set response content type
    response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')

    # Set the filename for download
    response['Content-Disposition'] = f'inline; filename="{inquiry.customer.first_name}_{inquiry.customer.last_name}_quotation{inquiry.id}.pdf"'

    return response


def make_complain_view(request, id):

    inquiry = Inquiry.objects.get(id = id)

    if request.method == 'POST':
        opened = request.POST.get('open')
        detail = request.POST.get('detail')
        fixe_detail = request.POST.get('fixe_detail')
        closed = request.POST.get('closed')

        print(opened,detail,closed)

        try :
            complain = Complain.objects.get(inquiry=inquiry)
            print(complain)
            print("11111111111111")
            complain.opened = opened
            complain.detail = detail
            complain.fixe_detail = fixe_detail
            if closed:
                complain.closed = closed
                complain.save()
                return redirect('make_inq_done', inq_id = id)
            
            complain.save()
            return redirect('make_inq_complain', inq_id = id)
            
        except :
            print("222222222222222")
            complain = Complain.objects.create(inquiry=inquiry)
            complain.opened = opened
            complain.detail = detail
            complain.fixe_detail = fixe_detail
            if closed:
                complain.closed = closed
                complain.save()
                return redirect('make_inq_done', inq_id = id)
            
            complain.save()
            return redirect('make_inq_complain', inq_id = id)

    return redirect('inquiry_info', id = id)


def messages_view(request, id):

    inquiry = Inquiry.objects.get(id = id)

    # delete the notification for this inquiry id
    try :
        the_notifications = MessageNotify.objects.filter(inquiry=inquiry)
        for notify in the_notifications:
            if notify.employee.user == request.user:
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
        sp = inquiry.sp
        employees = Employee.objects.filter(sp=inquiry.sp)
        
        for employee in employees:
            message = Message.objects.create(
                inquiry = inquiry,
                source = source,
                destination = employee ,
                content = content
            )

        if request.user.employee.position.name == "call center": 
            #create notification
            all_employees = Employee.objects.filter(sp=inquiry.sp)
            for employee in all_employees:
                notification = MessageNotify(
                    employee = employee,
                    inquiry = inquiry,
                    service = inquiry.services,
                    sp = inquiry.sp
                )
                notification.save()

                isnotify = IsEmployeeReadMessage(
                            employee = employee,
                            notified = False,
                            sp = inquiry.sp
                        )
                isnotify.save()

        elif request.user.employee.position.name == "super provider":
            position = Position.objects.get(name='call center')
            all_employees = Employee.objects.filter(position=position)
            for employee in all_employees:
                notification = MessageNotify(
                        employee = employee,
                        inquiry = inquiry,
                        service = inquiry.services,
                        sp = inquiry.sp
                    )
                notification.save()


                isnotify = IsEmployeeReadMessage(
                            employee = employee,
                            notified = False,
                            sp = inquiry.sp
                        )
                isnotify.save()

    booking = Booking.objects.filter(inquiry=inquiry)
    messages = Message.objects.filter(inquiry=inquiry)
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {
        'position': request.user.employee.position,
        'layout_path': layout_path,
        'notifications':notifications,
        'notifications_counter':notifications_counter,
        'messages': messages, 
        'inquiry':inquiry,
        'messages':messages,
        'messages_counter':messages_counter,
        "booking":booking,

        }
    context = TemplateLayout.init(request, context)
    return render(request, 'messages/message.html', context)
        
