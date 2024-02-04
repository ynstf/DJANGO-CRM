from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

class AuthView(TemplateView):
    template_name = "auth_login_basic.html"  # Set your template name here
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Update the context
        context.update({
            "layout_path": TemplateHelper.set_layout("layout_blank.html", context),
        })

        return context

    def post(self, request, *args, **kwargs):
        # Handle POST request for user login
        username = request.POST.get('email-username')
        password = request.POST.get('password')

        print(username,password)

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # User is authenticated, log them in
            login(request, user)
            print(True)
            return redirect('dashboard')  # Replace 'dashboard' with your actual URL name
        else:
            # Authentication failed, display an error message
            print(False)
            messages.error(request, 'Invalid username or password')
            
        # Set the layout path even when authentication fails
        layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
        context = {'layout_path': layout_path}

        return render(request, self.template_name, context)

    
    def dispatch(self, request, *args, **kwargs):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Redirect to the dashboard or any other URL
            return redirect('dashboard')  # Replace 'dashboard' with your actual URL name

        return super().dispatch(request, *args, **kwargs)


