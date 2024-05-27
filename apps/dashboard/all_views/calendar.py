from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from apps.dashboard.models import Booking, InquiryReminder, InquiryNotify
from django.shortcuts import render
import json

def calendar_view(request):
    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()
    
    # Example dates you want to highlight on the calendar
    dates_with_reminders = []


    reminders = InquiryReminder.objects.all()
    if request.user.employee.position.name == 'super provider':
        reminders = reminders.filter(inquiry__sp=request.user.employee.sp)

    for r in reminders :
        dates_with_reminders.append(r.schedule)

    data = []
    for date in dates_with_reminders:
        ids = []
        for ir in InquiryReminder.objects.filter(schedule=date):
            ids.append(ir.inquiry.id)
        # Convert date to ISO format
        date_iso = date.isoformat()
        data.append({'date': date_iso, 'ids': ids, 'count': len(ids)})  # Use len(ids) instead of count()

    # Convert data to JSON
    dates_json = json.dumps(data)
    
    # Pass the dates to the template
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {
        'position': request.user.employee.position,
        'layout_path': layout_path,
        'notifications': notifications,
        'notifications_counter': notifications_counter,
        'dates_json': dates_json
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