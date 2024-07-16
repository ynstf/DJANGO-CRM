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
    InquiryStatus, IsEmployeeNotified, Language, Nationality, Quotation, Source, Status, Request,
    SuperProvider)
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.urls import reverse
from urllib.parse import quote
from datetime import timedelta
from apps.dashboard.models import Landline, WhatsApp, Emirate, QuotationForm, Advence, Invoice, Complain, Message, MessageNotify, IsEmployeeReadMessage, Points, Address
import cloudinary
import cloudinary.uploader
import json
from datetime import datetime
from django.contrib import messages as msgs
from django.db.models import Q
from django.utils import timezone

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
        try:
            data = i.address.location.split(',')
        except:
            data = []
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


@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['call_center']).exists() )
def inq_from_points(request):

    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()
    messages = MessageNotify.objects.filter(employee=request.user.employee)
    messages_counter = messages.count()

    points = Points.objects.all()

    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'position': request.user.employee.position,
            'layout_path': layout_path,
            'notifications':notifications,
            'notifications_counter':notifications_counter,
            'messages':messages,
            'messages_counter':messages_counter,
            'points':points

            }
    context = TemplateLayout.init(request, context)
    return render(request, "inquiry/points.html", context)

@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['call_center']).exists() )
def cancel_point(request,id):
    point = Points.objects.get(id = id)
    point.approved = "F"
    point.save()
    return redirect('from_points')


@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['call_center']).exists() )
def add_inq_from_points(request,id):

    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()
    messages = MessageNotify.objects.filter(employee=request.user.employee)
    messages_counter = messages.count()

    point = Points.objects.get(id = id)

    # delete the notification for this inquiry id
    try :
        the_notifications = InquiryNotify.objects.filter(point=point)
        for notify in the_notifications:
            if notify.employee.user == request.user:
                notify.delete()
                notify_info = IsEmployeeNotified.objects.filter(employee = request.user.employee)
                notify_info.delete()
    except :
        pass

    if request.method == 'POST':
        #customer fields

        #contact fields
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        nationality_id = request.POST.get('nationality')
        language_id = request.POST.get('language')
        trn = request.POST.get('trn')


        phone_form = request.POST.getlist('customer-phone_numbers')
        whatsapp_form = request.POST.getlist('customer-whats_apps')
        landline_form = request.POST.getlist('customer-landlines')
        email_form = request.POST.getlist('customer-emails')
        
        merge_option = request.POST.get('merge_option')
        merge = merge_option == 'yes'
        adress_name = request.POST.get('address-address_name')
        adress_type = request.POST.get('address-type')
        emarate = request.POST.get('address-emirate')
        adress_desc = request.POST.get('address-description_location')
        location = request.POST.get('address-location')
        inq_date = request.POST.get('inquiry-date_inq')
        inq_source = request.POST.get('customer-source')
        inq_service = request.POST.get('inquiry-services')
        team_leader = request.POST.get('inquiry-team_leader')
        sp = request.POST.get('inquiry-superprovider')
        remainder_checked = request.POST.get('remainder_check')
        schedule_time = request.POST.get('inquiry-reminder')
        inq_desc = request.POST.get('inquiry-description')

        user_already_exist = False
        common_element = set(phone_form) & set(list(PhoneNumber.objects.values_list('number',flat=True)))
        if merge and common_element and '+971' not in set(phone_form) :
            phone = list(common_element)[0]
            print('already exist :',phone)
            customer = PhoneNumber.objects.get(number = phone).customer
            user_already_exist = True
            print(customer.first_name)
        else:
            # Find the nationality and language instances
            nationality = Nationality.objects.get(id=nationality_id) if nationality_id else None
            language = Language.objects.get(id=language_id) if language_id else None

            # Save the customer
            # Create the customer
            customer = Customer.objects.create(
                                employee = Employee.objects.get(user=request.user),
                                first_name=first_name,
                                last_name=last_name,
                                gender=gender,
                                nationality=nationality,
                                language=language,
                                trn=trn
                            )



            # Save the emails
            for e in email_form:
                email = Email(customer=customer,email=e)
                email = email.save() 

            # Save the phones
            for p in phone_form:
                phone = PhoneNumber(customer=customer,number=p)
                phone = phone.save()

            # Save the whatsapps
            for w in whatsapp_form:
                whatsapp = WhatsApp(customer=customer,whatsapp=w)
                whatsapp = whatsapp.save()

            # Save the landlines
            for l in landline_form:
                landline = Landline(customer=customer,landline=l)
                landline = landline.save()

            try:
                coords = location.split(",")
                latitude = coords[0]
                longitude = coords[1]
            except:
                latitude = 0
                longitude = 0

            google_maps_link = f"https://www.google.com/maps?q={latitude},{longitude}"

            if emarate and adress_type :
                address = Address(
                    customer=customer,
                    address_name=adress_name,
                    type=adress_type,
                    emirate=Emirate.objects.get(id=emarate),  # Replace with the actual Emirate retrieval
                    description_location=adress_desc,
                    location=location,
                    location_url=google_maps_link,
                )
                address.save()
            else:
                if emarate=="" and adress_type=="" :
                    address = Address(
                    customer=customer,
                    address_name=adress_name,
                    description_location=adress_desc,
                    location=location,
                    location_url=google_maps_link,
                    )
                    address.save()
                else:
                    if emarate=="":
                        address = Address(
                            customer=customer,
                            address_name=adress_name,
                            type=adress_type,
                            description_location=adress_desc,
                            location=location,
                            location_url=google_maps_link,
                        )
                        address.save()

                    if adress_type=="" :
                        address = Address(
                            customer=customer,
                            address_name=adress_name,
                            emirate=Emirate.objects.get(id=emarate),  # Replace with the actual Emirate retrieval
                            description_location=adress_desc,
                            location=location,
                            location_url=google_maps_link,
                        )
                    
                        address.save()

            #
            services_set = Service.objects.get(name=inq_service)
            #owner = Employee.objects.get(id=inq_employees[q])
            team = Employee.objects.get(id=team_leader)
            current_inq_source_id = inq_source
            current_inq_source = Source.objects.get(id=current_inq_source_id)
            current_sp = SuperProvider.objects.get(id=sp)

            inquiry = Inquiry(
                            customer=customer,
                            address=address,
                            source = current_inq_source,
                            services=services_set,
                            sp=current_sp,
                            description=inq_desc,
                            #owner=owner,
                            team_leader=team,
                            )
            inquiry.save()

            inq_employees = request.POST.getlist(f'inquiry-employees')
            
            for id_employee in inq_employees:
                owner = Employee.objects.get(id=id_employee)
                inquiry.handler.add(owner)
                
                notification = InquiryNotify(
                    employee = owner,
                    inquiry = inquiry,
                    sp = current_sp,
                    action = "new"
                )
                notification.save()

                isnotify = IsEmployeeNotified(
                    employee = owner,
                    notified = False
                )
                isnotify.save()

            inquiry.save()



            new = Status.objects.get(name = "new")
            inq_state = InquiryStatus(
                inquiry = inquiry,
                status= new
            )
            inq_state.newDelay = timezone.now()
            inq_state.save()


            req = Request(
                inquiry = inquiry,
                demande = "by call center"
            )
            req.save()
        
        
        if remainder_checked == "on":
            employee_id = request.user.employee.id
            employee = Employee.objects.get(id=employee_id)
            reminder = InquiryReminder(
                employee = employee,
                inquiry=inquiry,
                service=services_set,
                gool='inquiry',
                schedule=schedule_time
            )
            reminder.save()

        point.approved = "T"
        point.inquiry = inquiry
        point.save()
        return redirect('from_points')


    # selection fields
    Sources = Source.objects.all()
    Genders = [{'gender':"Male",'id':'male'},
                {'gender':"Female",'id':'female'}]
    Nationalities = Nationality.objects.all()
    Services = Service.objects.all()
    Languages = Language.objects.all()
    types = [{'type':"House",'id':'house'},
                {'type':"Company",'id':'company'}]
    Emirates = Emirate.objects.all()
    all_sp = SuperProvider.objects.all()

    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'position': request.user.employee.position,
            'layout_path': layout_path,
            'notifications':notifications,
            'notifications_counter':notifications_counter,
            'messages':messages,
            'messages_counter':messages_counter,
            'point':point,

            'Sources':Sources,
            'Genders':Genders,
            'Nationalities':Nationalities,
            'Services':Services,
            'Languages':Languages,
            'Emirates':Emirates,
            'types':types,
            'all_sp':all_sp,
            'team_leaders':Employee.objects.filter(position=Position.objects.get(name='team leader')),

            }
    context = TemplateLayout.init(request, context)
    return render(request, "inquiry/add_inq_point.html", context)

def make_inq_cancel(request,inq_id):
    if request.method == 'POST':
        canceling_causes = request.POST.get('canceling_causes')

    cancel = Status.objects.get(name = "cancel")
    inquiry = Inquiry.objects.get(id = inq_id)
    inq_state = InquiryStatus.objects.get(inquiry = inquiry)
    inq_state.status = cancel
    inq_state.cancelDelay = timezone.now()
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
    inq_state.newDelay = timezone.now()

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
    inq_state.connectDelay = timezone.now()
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
    sendQ  = Status.objects.get(name = "send Q")
    inquiry = Inquiry.objects.get(id = inq_id)
    inq_state = InquiryStatus.objects.get(inquiry = inquiry)
    inq_state.status = sendQ
    inq_state.sendqDelay = timezone.now()
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

def make_inq_sendB(request,inq_id):
    sendB  = Status.objects.get(name = "send B")
    inquiry = Inquiry.objects.get(id = inq_id)
    inq_state = InquiryStatus.objects.get(inquiry = inquiry)
    inq_state.status = sendB
    inq_state.sendbDelay = timezone.now()
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
            action = "send bill"
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
    inq_state.pendingDelay = timezone.now()
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
    inq_state.doneDelay = timezone.now()
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

def make_action(request,inq_id):
    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()

    inquiry = Inquiry.objects.get(id=inq_id)


    if request.method == 'POST':
        action = request.POST.get('inquiry_action')
        print(action)

        req = Request(
            inquiry = inquiry,
            demande = action
        )
        req.save()

        new = Status.objects.get(name = "new")
        inq_state = InquiryStatus.objects.get(inquiry=inquiry)
        inq_state.status = new
        inq_state.save()

        #all_employees = Employee.objects.filter(sp=current_sp)
        
        #for employee in all_employees:
        for owner in inquiry.handler.all():
            notification = InquiryNotify(
                employee = owner,
                inquiry = inquiry,
                sp = inquiry.sp,
                action = "new"
            )
            notification.save()

        for owner in inquiry.handler.all():
            isnotify = IsEmployeeNotified(
                employee = owner,
                notified = False
            )
            isnotify.save()

        
        msgs.success(request, f"you add new request for {action} to record owners.")

        return redirect("inquiry_info",id=inq_id)

    # Render the initial page with the full customer list
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'position': request.user.employee.position,
                'layout_path': layout_path,
                'notifications':notifications,
                'notifications_counter':notifications_counter,
                "states":Status.objects.all(),

                
                }
    

    context = TemplateLayout.init(request, context)
    return render(request, 'inquiry/make_action.html',context)

def get_messages(request):
    try:
        messages = MessageNotify.objects.filter(employee=request.user.employee)
        messages_counter = messages.count()
    except:
        messages = []
        messages_counter = 0
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


    try:
        notifications = InquiryNotify.objects.filter(employee=request.user.employee)
        notifications_counter = notifications.count()
    except:
        notifications = []
        notifications_counter = 0

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

            inquiries = inquiries.filter(handler=request.user.employee)
        except:
            pass


        search_counter = inquiries.count()

        try :
            search_number = request.user.employee.search_number
            #order inquiries by last updated

            date_limit = timezone.now() - timedelta(days=int(search_number))
            inquiries = inquiries.filter(date_inq__gte=date_limit)
            
            inquiries = inquiries.order_by('-inquirystatus__update')
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
            
        reqs = Request.objects.filter(inquiry=i) 

        try:
            stt = InquiryStatus.objects.get(inquiry=i)
            act = EmployeeAction.objects.filter(inquiry=i).last()
            

            newDelay = stt.newDelay 
            connectDelay = stt.connectDelay 
            underproccessDelay = stt.underproccessDelay 
            sendqDelay = stt.sendqDelay 
            pendingDelay = stt.pendingDelay 
            sendbDelay = stt.sendbDelay 
            doneDelay = stt.doneDelay
            cancelDelay = stt.cancelDelay


            new_connect = (connectDelay - newDelay) if newDelay is not None and connectDelay is not None and connectDelay > newDelay else '_'
            connect_sendqDelay = (sendqDelay - connectDelay) if sendqDelay is not None and connectDelay is not None and sendqDelay > connectDelay else '_'
            sendqDelay_underproccessDelay = (underproccessDelay - sendqDelay) if underproccessDelay is not None and sendqDelay is not None and underproccessDelay > sendqDelay else '_'
            underproccessDelay_sendbDelay = (sendbDelay - underproccessDelay) if sendbDelay is not None and underproccessDelay is not None and sendbDelay > underproccessDelay else '_'
            
            sendqDelay_pendingDelay = (pendingDelay - sendqDelay) if sendqDelay is not None and pendingDelay is not None and pendingDelay > sendqDelay else '_'
            connect_underproccessDelay = (underproccessDelay - connectDelay) if underproccessDelay is not None and connectDelay is not None and underproccessDelay > connectDelay else '_'
            sendbDelay_doneDelay = (doneDelay - sendbDelay) if doneDelay is not None and sendbDelay is not None and doneDelay - sendbDelay else '_'

            
            inquiry.append({'info':i,
                            'state':stt,
                            'advence' : advence,
                            'totale':totale,
                            'action':act,
                            'requests':reqs,
                            
                            'connect_sendqDelay': connect_sendqDelay,
                            'new_connect': new_connect,
                            'sendqDelay_underproccessDelay': sendqDelay_underproccessDelay,
                            'underproccessDelay_sendbDelay': underproccessDelay_sendbDelay,
                            'sendqDelay_pendingDelay': sendqDelay_pendingDelay,
                            'connect_underproccessDelay': connect_underproccessDelay,
                            'sendbDelay_doneDelay': sendbDelay_doneDelay,

                        })
        except:
            inquiry.append({'info':i,
                        })

    try:
        cols = request.user.employee.columns.split("*,*")
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
    msgs = MessageNotify.objects.filter(employee=request.user.employee)
    messages_counter = msgs.count()

    inquiry = Inquiry.objects.get(id=id)
    inquiry_state = InquiryStatus.objects.get(inquiry=inquiry)
    customer = inquiry.customer
    requests = Request.objects.filter(inquiry=inquiry)

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
    try:
        quotations = requests.last()
        quotations = quotations.quotation.all()
        for quotation in quotations:
            line = quotation.data.split(',*,')
            inquiry_data.append(line)
    except:
        pass


    try:
        # Assuming you want to include a predefined message
        phone_number = customer.whatsapp_set.all().first().whatsapp
    except :
        phone_number = ""
    


    # quotations
    history_data = []
    for r in requests.order_by('-id'):
        quotations = r.quotation.all()
        lines = []
        for quotation in quotations:
            line = quotation.data.split(',*,')
            lines.append(line)

        # whatsapp urls for this request
        ## make message for this request quotations
        message = "Your Quotations ready, check the link"
        pdf_url = reverse('generate_pdf', args=[r.id])
        absolute_pdf_url = request.build_absolute_uri(pdf_url)
        whatsapp_link_quotation = f'https://api.whatsapp.com/send?phone={phone_number}&text={quote(message)}%0A{quote(str(absolute_pdf_url))}'

        history_data.append({"whatsapp_link":whatsapp_link_quotation, "request":r, 'inquiry_data':lines })


    # bookings
    history_book = []
    history_books = requests.order_by('-id')
    for r in history_books:
        ## make message for this request invoice
        message = "Your Invoice ready, check the link"
        pdf_url = reverse('generate_invoice', args=[r.id])
        absolute_pdf_url = request.build_absolute_uri(pdf_url)
        whatsapp_link_invoice = f'https://api.whatsapp.com/send?phone={phone_number}&text={quote(message)}%0A{quote(str(absolute_pdf_url))}'
        history_book.append({"book":r, "whatsapp_link_invoice":whatsapp_link_invoice})

    
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


    # make message for inquiry
    message = "Your Quotations ready, check the link"
    pdf_url = reverse('generate_pdf', args=[id])
    absolute_pdf_url = request.build_absolute_uri(pdf_url)
    whatsapp_link = f'https://api.whatsapp.com/send?phone={phone_number}&text={quote(message)}%0A{quote(str(absolute_pdf_url))}'


    message = "Your Invoice ready, check the link"
    pdf_url = reverse('generate_invoice', args=[id])
    absolute_pdf_url = request.build_absolute_uri(pdf_url)
    whatsapp_link_invoice = f'https://api.whatsapp.com/send?phone={phone_number}&text={quote(message)}%0A{quote(str(absolute_pdf_url))}'

    
    connect_with_customer_whatsapp_link = f'https://api.whatsapp.com/send?phone={phone_number.replace("+","")}'


    try:
        complain = Complain.objects.get(inquiry=inquiry)
    except:
        complain = None


    status = []
    call_center_actions = ['pending','new','cancel','done','complain','underproccess']
    service_provider_actions = ['connecting','send Q','send B','underproccess','new']
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
            'msgs':msgs,
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
            'requests':requests,
            'history_data':history_data,
            'history_book':history_book


            }
    

    context = TemplateLayout.init(request, context)
    return render(request, "inquiry/inquiries_info.html", context)


@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['provider', 'admin', 'call_center']).exists() or (Permission.objects.get(name="make quotation") in u.employee.permissions.all()) )
def make_quotation_view(request, id):
    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()
    messages = MessageNotify.objects.filter(employee=request.user.employee)
    messages_counter = messages.count()



    if request.method == 'POST':

        """quotation_service = request.POST.get('quotation-service')
        sp = request.POST.get('quotation-sp')"""

        


        quotation_date = request.POST.get('quotation-date')


        inquiry = Inquiry.objects.get(id=id)
        
        quotation_service = inquiry.services.id
        sp = inquiry.sp.id

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

        req = Request.objects.filter(inquiry=inquiry).last()

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

            try :
                req.quotation.add(quotation)
                req.save()
            except:
                req = Request(
                    inquiry = inquiry,
                    demande = "by call center",
                    aproved = True
                )
                req.save()
                req.quotation.add(quotation)
                req.save()

        
        return redirect('make_inq_sendQ', inq_id=id)




    inquiry = Inquiry.objects.get(id=id)
    # Retrieve the Service instance
    service_instance = inquiry.services
    # Convert the comma-separated string back to a list
    columns_list = service_instance.columns.split(',')

    #sp = request.user.employee.sp
    sp = inquiry.sp
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
@user_passes_test(lambda u: u.groups.filter(name__in=['provider', 'admin', 'call_center']).exists() or (Permission.objects.get(name="make quotation") in u.employee.permissions.all()) )
def edit_quotation_view(request, id):
    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()
    messages = MessageNotify.objects.filter(employee=request.user.employee)
    messages_counter = messages.count()

    req = Request.objects.get(id = id)
    inquiry = req.inquiry
    quotations = req.quotation.all()


    if request.method == 'POST':

        #quotation_service = request.POST.get('quotation-service')
        #sp = request.POST.get('quotation-sp')
        quotation_date = request.POST.get('quotation-date')

        quotation_service = inquiry.services.id
        sp = inquiry.sp.id

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

        #delete old values
        quots = req.quotation.all()
        quots.delete()

        for i in range(len(lent)):
            data = []
            for field in columns_list:
                details = request.POST.getlist(f'quotation-{field}')[i]
                data.append(details)
            total = float(data[-1])*float(data[-2])
            columns_str = ",*,".join(data)
            print(columns_str)

            print(data)
            
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

            req.quotation.add(quotation)

            if request.user.employee.position.name == 'super provider':
                req.aproved = False
                # notify all cc and admins
                cc = Position.objects.get(name="call center")
                admin = Position.objects.get(name="admin")
                all_employees = Employee.objects.filter(Q(position=cc) | Q(position=admin))
                #create notification
                for employee in all_employees:
                    notification = InquiryNotify(
                        employee = employee,
                        inquiry = inquiry,
                        service = inquiry.services,
                        action = "need approve"
                    )
                    notification.save()
                    isnotify = IsEmployeeNotified(
                        employee = employee,
                        notified = False
                    )
                    isnotify.save()

            req.save()


        
        return redirect('inquiry_info', id=inquiry.id)




    # Retrieve the Service instance
    service_instance = inquiry.services
    # Convert the comma-separated string back to a list

    columns_list = service_instance.columns.split(',')

    
    last_data = []
    for quotation in quotations:
        last_data.append([d for d in quotation.data.split(",*,")])

    
    last = []
    n=0
    for data,q in zip(last_data,quotations):
        line = []
        for d,c in zip(data,columns_list):
            dic = {}
            dic["name"] = c
            dic["value"] = d
            line.append(dic)
        n+=1
        last.append({'id':q.id,'n':n,'data':line})




    #sp = request.user.employee.sp
    sp = inquiry.sp
    services = sp.service.all()
    date=quotations[0].quotation_date

    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'position': request.user.employee.position,
            'layout_path': layout_path,
            'notifications':notifications,
            'notifications_counter':notifications_counter,
            'date':date,
            'customer': inquiry.customer,
            'inquiry': inquiry,
            'services':services,
            'sp':sp,
            'columns_list':columns_list,
            'messages':messages,
            'messages_counter':messages_counter,
            'last_data':last_data,
            'last':last,
            }
    context = TemplateLayout.init(request, context)
    return render(request, "inquiry/edit_quotation.html", context)



def make_approvment(request, req_id):
    req = Request.objects.get(id = req_id)
    req.aproved = True
    req.save()

    inquiry = req.inquiry

    #create notification
    for employee in inquiry.handler.all():
        notification = InquiryNotify(
            employee = employee,
            inquiry = inquiry,
            service = inquiry.services,
            action = "approvement"
        )
        notification.save()
        isnotify = IsEmployeeNotified(
            employee = employee,
            notified = False
        )
        isnotify.save()

    return redirect('inquiry_info', id=inquiry.id) 


@login_required(login_url='/')
def edit_inquiry(request,id):
    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()
    messages = MessageNotify.objects.filter(employee=request.user.employee)
    messages_counter = messages.count()
    inquiry = Inquiry.objects.get(id = id)
    inquiry_state = InquiryStatus.objects.get(inquiry=inquiry)

    if request.method == 'POST':
        inq_source = request.POST.get('customer-source')
        inq_service = request.POST.get('inquiry-services')
        team_leader = request.POST.get('inquiry-team_leader')
        #inq_employees = request.POST.get('inquiry-employees')
        sp = request.POST.get('inquiry-superprovider')
        inq_desc = request.POST.get('inquiry-description')

        owners = request.POST.getlist('inq-owner')

        srv = Service.objects.get(number=inq_service)
        src = Source.objects.get(id=inq_source)
        tl = Employee.objects.get(id=team_leader)
        sup = SuperProvider.objects.get(id=sp)
        #owner = Employee.objects.get(id=inq_employees)
        desc = inq_desc

        print("service:" ,srv)
        print("source :",src)
        print("team :",tl)
        print("sp: ",sup)
        print("desc:",desc)
        #print("owner",owner)

        inquiry.services = srv
        inquiry.source = src
        inquiry.sp = sup
        #inquiry.owner = owner
        inquiry.description = desc
        inquiry.team_leader = tl



        inquiry.save()

        for owner in owners:
            print('owner::::::::::::::',owner)
            employee = Employee.objects.get(id=owner)
            inquiry.handler.add(employee)
            
            notification = InquiryNotify(
                employee = employee,
                inquiry = inquiry,
                sp = sup,
                action = "new"
            )
            notification.save()

            isnotify = IsEmployeeNotified(
                employee = employee,
                notified = False
            )
            isnotify.save()
        inquiry.save()


        return redirect("inquiry_info",id=id)


    status = []
    call_center_actions = ['pending','new','cancel','done','complain','underproccess']
    service_provider_actions = ['connecting','send Q','send B','underproccess','new']
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
                'inquiry': Inquiry.objects.get(id=id),
                'handlers': Inquiry.objects.get(id=id).handler.all(),
                'sps': Employee.objects.filter(sp=inquiry.sp),


                'services':Service.objects.all(),
                'messages':messages,
                'messages_counter':messages_counter,
                'all_sp':SuperProvider.objects.all(),
                'Sources':Source.objects.all(),
                'team_leaders':Employee.objects.filter(position=Position.objects.get(name='team leader')),
                'status':status,
                'inquiry_state':inquiry_state,

                }
    
    context = TemplateLayout.init(request, context)
    return render(request, 'inquiry/edit_inquiry.html',context)


def generate_pdf_view(request, request_id):
    # Retrieve the inquiry and associated quotations

    req = Request.objects.get(id = request_id)
    inquiry = req.inquiry
    quotations = req.quotation.all()

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
        
