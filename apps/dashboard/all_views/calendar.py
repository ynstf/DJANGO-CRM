from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from apps.dashboard.models import Booking, InquiryReminder, InquiryNotify, Status
from apps.dashboard.models_com import SuperProvider, Service
from django.shortcuts import render
import json

def calendar_view(request):
    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()

    status = request.GET.get('status')
    service = request.GET.get('service')
    sp = request.GET.get('sp')

    search_str = {}

    reminders = InquiryReminder.objects.all()

    if status :
        st = Status.objects.get(id=status)
        reminders = reminders.filter(inquiry__inquirystatus__status=st)
        status=int(status)
        search_str["status"]=status
    
    if service :
        reminders = reminders.filter(inquiry__services=service)
        service = int(service)
        search_str["service"]=service
    
    if sp :
        reminders = reminders.filter(inquiry__sp=sp)
        sp = int(sp)
        search_str["sp"]=sp
    
    # Example dates you want to highlight on the calendar
    dates_with_reminders = []


    if request.user.employee.position.name == 'super provider':
        reminders = reminders.filter(inquiry__sp=request.user.employee.sp)

    for r in reminders :
        dates_with_reminders.append(r.schedule)

    data = []
    
    for date in dates_with_reminders:
        ids = []
        types = []
        for ir in reminders.filter(schedule=date):
            ids.append(ir.inquiry.id)
            types.append(ir.gool)
        # Convert date to ISO format
        date_iso = date.isoformat()
        data.append({'date': date_iso, 'types':types, 'ids': ids, 'count': len(ids)})  # Use len(ids) instead of count()

    # Convert data to JSON
    dates_json = json.dumps(data)
    
    # Pass the dates to the template
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {
        'position': request.user.employee.position,
        'layout_path': layout_path,
        'notifications': notifications,
        'notifications_counter': notifications_counter,
        'dates_json': dates_json,
        'services':Service.objects.all(),
        'states':Status.objects.all(),
        'service_providers':SuperProvider.objects.all(),
        'search_str':search_str,
    }
    context = TemplateLayout.init(request, context)
    return render(request, 'calendar.html', context)


def reminder_day_view(request,date):
    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()
    
    inquiries=[]
    for ir in InquiryReminder.objects.filter(schedule=date):
            inquiries.append(ir.inquiry)

    
    # Pass the dates to the template
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {
        'position': request.user.employee.position,
        'layout_path': layout_path,
        'notifications': notifications,
        'notifications_counter': notifications_counter,
        'inquiries':inquiries,
        'date':date,
    }
    context = TemplateLayout.init(request, context)
    return render(request, 'reminder_day.html', context)