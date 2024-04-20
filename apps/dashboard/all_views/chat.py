from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from apps.dashboard.models import Message
from django.utils import timezone

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



    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'title':title,
                'position': request.user.employee.position,
                'layout_path': layout_path,
                'messages': inquiries_list,


                }
    context = TemplateLayout.init(request, context)
    return render(request, 'chat/chat_page.html', context)
