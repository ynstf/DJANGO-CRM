from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from apps.authentication.models import Employee
from django.shortcuts import render, redirect
from .forms import CustomerForm, AddressForm, InquiryForm
from .models import Customer, Nationality
from django.contrib.auth.decorators import login_required

# Create your views here.
def dashboard(request):

    # Set the layout path even when authentication fails
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'layout_path': layout_path}


    return render(request, "dash.html", context)


from django.forms import formset_factory
def customer_list(request):
    customers = Customer.objects.all()

    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'layout_path': layout_path,
                'customers': customers}
    
    return render(request, 'customer_list.html', context)

@login_required(login_url='/')
def add_customer(request):
    if request.method == 'POST':
        customer_form = CustomerForm(request.POST, prefix='customer')
        address_form = AddressForm(request.POST, prefix='address')
        inquiry_form = InquiryForm(request.POST, prefix='inquiry')

        if customer_form.is_valid() and address_form.is_valid() and inquiry_form.is_valid():

            # Save the customer
            customer = customer_form.save(commit=False)  # Don't save yet, so we can set the employee
            customer.employee = Employee.objects.get(user=request.user)  # Set the employee
            customer.save()

            # Populate address form fields
            address_form.instance.customer = customer

            # Save the address
            address = address_form.save()

            # Populate inquiry form fields
            inquiry_form.instance.customer = customer
            inquiry_form.instance.address = address

            # Save the inquiry
            inquiry_form.save()

            return redirect('customer_list')  # Redirect to the customer list page
    else:
        # Creating instances of forms with prefixes
        customer_form = CustomerForm(prefix='customer')
        address_form = AddressForm(prefix='address')
        inquiry_form = InquiryForm(prefix='inquiry')

        # You can set default values for some fields if needed
        # For example, get the first nationality from the database
        default_nationality = Nationality.objects.first()
        if default_nationality:
            customer_form.fields['nationality'].initial = default_nationality

        # Similarly, set default values for other fields as needed
            
    # Set the layout path even when authentication fails
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'layout_path': layout_path,
                'customer_form': customer_form, 'address_form': address_form, 'inquiry_form': inquiry_form
                }

    return render(request, 'add_customer.html', context)
