from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from apps.authentication.models import Employee
from django.shortcuts import render, redirect
from apps.dashboard.models import Address, Inquiry
from .forms import CustomerForm, AddressForm, InquiryForm
from .models import Customer, Nationality
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# Create your views here.

def dashboard(request):

    # Set the layout path even when authentication fails
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'layout_path': layout_path}


    return render(request, "dash.html", context)

'''
def customer_list(request):
    customers = Customer.objects.all()

    # Handle search form submission
    if request.method == 'GET':
        # Get the name entered in the query parameter
        name_query = request.GET.get('name')
        
        # Filter customers based on the entered name
        if name_query:
            customers = customers.filter(first_name__icontains=name_query)

            return JsonResponse({'customers': customers})
    
    # Render the initial page with the full customer list
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'layout_path': layout_path, 'customers': customers}
    
    return render(request, 'customer_list.html', context)
'''

def customer_list(request):
    customers = Customer.objects.all()

    # Handle search form submission
    if request.method == 'GET':
        # Get the name entered in the query parameter
        name_query = request.GET.get('name')
        
        # Filter customers based on the entered name
        if name_query:
            customers = customers.filter(first_name__icontains=name_query)

            # If it's an AJAX request, return a JSON response
            if request.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                # Extract customer data and convert it to a list of dictionaries
                customer_data = [{customer} for customer in customers]

                # Return a JSON response with the customer data
                return JsonResponse({'customers': customer_data})

    # Render the initial page with the full customer list
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'layout_path': layout_path, 'customers': customers}
    
    return render(request, 'customer_list.html', context)

from .models import Email,PhoneNumber,WhatsApp,Landline

@login_required(login_url='/')
def add_customer(request):
    if request.method == 'POST':
        customer_form = CustomerForm(request.POST, prefix='customer')
        address_form = AddressForm(request.POST, prefix='address')
        inquiry_form = InquiryForm(request.POST, prefix='inquiry')

        phone_form = request.POST.get('customer-phone_numbers')
        whatsapp_form = request.POST.get('customer-whats_apps')
        landline_form = request.POST.get('customer-landlines')
        email_form = request.POST.get('customer-emails')
        print(email_form)

        if customer_form.is_valid() and address_form.is_valid() and inquiry_form.is_valid():

            # Save the customer
            customer = customer_form.save(commit=False)  # Don't save yet, so we can set the employee
            customer.employee = Employee.objects.get(user=request.user)  # Set the employee
            customer.save()

            # Save the email
            email = Email(customer=customer,email=email_form)
            email = email.save() 

            # Save the phone
            phone = PhoneNumber(customer=customer,number=phone_form)
            phone = phone.save()

            # Save the whatsapp
            whatsapp = WhatsApp(customer=customer,number=whatsapp_form)
            whatsapp = whatsapp.save()

            # Save the landline
            landline = Landline(customer=customer,number=landline_form)
            landline = landline.save()

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



from django.shortcuts import render, get_object_or_404


def customer_info(request, id):
    customer = get_object_or_404(Customer, id=id)
    addresses = Address.objects.filter(customer=customer)
    inquiries = Inquiry.objects.filter(address__in=addresses)


    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'layout_path': layout_path,
            'customer': customer,
            'addresses': addresses,
            'inquiries': inquiries,
            }

    return render(request, "customer_info.html", context)
