from django.shortcuts import render
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper

# Create your views here.
def dashboard(request):

    # Set the layout path even when authentication fails
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'layout_path': layout_path}


    return render(request, "dash.html", context)
