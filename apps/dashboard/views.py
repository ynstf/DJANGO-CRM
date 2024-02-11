from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from apps.authentication.models import Employee
from django.shortcuts import render, redirect

from apps.dashboard.models import Address, Customer, Inquiry
from .forms import CustomerForm, AddressForm, InquiryForm,CustomerFormEdit

from apps.dashboard.models import PhoneNumber, Email, Landline, WhatsApp, Emirate
from .forms import PhoneNumberForm, EmailForm, LandlineForm, WhatsAppForm

from .models import Customer, Nationality
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Email,PhoneNumber,WhatsApp,Landline
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView

# Create your views here.

def dashboard(request):
    context={
    }
    context = TemplateLayout.init(request, context)
    return render(request, 'dashboard.html',context)


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

                # show all detail
                customer = []
                for c in customers:
                    customer.append({'info':c,
                        'number':PhoneNumber.objects.filter(customer=c).first(),
                        'email':Email.objects.filter(customer=c).first(),
                        })
                print(customer)

                # Return a JSON response with the customer data
                return JsonResponse({'customers':customer })

    # Render the initial page with the full customer list
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})

    # show all phones in cases
    customer = []
    for c in customers:
        customer.append({'info':c,
                        'number':PhoneNumber.objects.filter(customer=c).first(),
                        'email':Email.objects.filter(customer=c).first(),
                        })
    print(customer)

    context = {'layout_path': layout_path,
                'customers': customer,

                }
    

    context = TemplateLayout.init(request, context)
    return render(request, 'customer_list.html', context)


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
            whatsapp = WhatsApp(customer=customer,whatsapp=whatsapp_form)
            whatsapp = whatsapp.save()

            # Save the landline
            landline = Landline(customer=customer,landline=landline_form)
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
    
    context = TemplateLayout.init(request, context)
    return render(request, 'add_customer.html', context)


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
    context = TemplateLayout.init(request, context)
    return render(request, "customer_info.html", context)


def delete_number(request, id_number):
    phone = get_object_or_404(PhoneNumber, id=id_number)
    id = phone.customer.id
    phone.delete()
    return redirect('edit_customer', id=id)

def delete_whatsApp(request, id_number):
    whatsApp = get_object_or_404(WhatsApp, id=id_number)
    id = whatsApp.customer.id
    whatsApp.delete()
    return redirect('edit_customer', id=id)

def delete_email(request, id_mail):
    mail = get_object_or_404(Email, id=id_mail)
    id = mail.customer.id
    mail.delete()
    return redirect('edit_customer', id=id)

def delete_landline(request, id_number):
    landline = get_object_or_404(Landline, id=id_number)
    id = landline.customer.id
    landline.delete()
    return redirect('edit_customer', id=id)

def delete_address(request, id_address):
    address = get_object_or_404(Address, id=id_address)
    id = address.customer.id
    address.delete()
    return redirect('edit_customer', id=id)




def edit_customer(request, id):
    customer = get_object_or_404(Customer, id=id)
    
    if request.method == 'POST':
        form = CustomerFormEdit(request.POST, instance=customer)
        

        #update number
        pre_numbers = PhoneNumber.objects.filter(customer=customer)
        pre_numbers.delete()
        numbers = request.POST.getlist("number")
        print(numbers)
        for number in numbers:
            new = PhoneNumber(customer = customer,
                                number =number)
            new.save()
        
        #update whatsapp
        pre_numbers = WhatsApp.objects.filter(customer=customer)
        pre_numbers.delete()
        numbers = request.POST.getlist("whatsapp")
        print(numbers)
        for number in numbers:
            new = WhatsApp(customer = customer,
                                whatsapp =number)
            new.save()

        #update Landline
        pre_numbers = Landline.objects.filter(customer=customer)
        pre_numbers.delete()
        numbers = request.POST.getlist("landline")
        print(numbers)
        for number in numbers:
            new = Landline(customer = customer,
                                landline =number)
            new.save()

        #update email
        pre_numbers = Email.objects.filter(customer=customer)
        pre_numbers.delete()
        numbers = request.POST.getlist("email")
        print(numbers)
        for number in numbers:
            new = Email(customer = customer,
                                email =number)
            new.save()



        #update address
        address = Address.objects.filter(customer=customer)
        address.delete()
        address_names = request.POST.getlist("address_name")
        types = request.POST.getlist("type")
        emirates = request.POST.getlist("emirate")
        description_locations = request.POST.getlist("description_location")
        locations = request.POST.getlist("location")
        for adrs in range(len(address_names)):
            try:
                print(emirates[adrs])
                emirate = Emirate.objects.get(id=emirates[adrs])
                print(emirate)
                new_address = Address(customer = customer,
                                        address_name = address_names[adrs],
                                        type = types[adrs],
                                        emirate = emirate, 
                                        description_location = description_locations[adrs], 
                                        location = locations[adrs])
                new_address.save()

            except:
                new_address = Address(customer = customer,
                                        address_name = address_names[adrs],
                                        type = types[adrs],
                                        description_location = description_locations[adrs], 
                                        location = locations[adrs])
                new_address.save()
                print(2)
        

        if form.is_valid():
            form.save()
            return redirect('customer_info', id=id)
    else:
        form = CustomerFormEdit(instance=customer)

        # show all phones in cases
        phone= PhoneNumber.objects.filter(customer=customer)
        phones = []
        for p in phone:
            phones.append({'form':PhoneNumberForm(instance=p),
                            'number':p})
        print(phones)
        
        #EmailForm, 
        # show all phones in cases
        email= Email.objects.filter(customer=customer)
        emails = []
        for e in email:
            emails.append({'form':EmailForm(instance=e),
                            'mail':e})
        print(emails)

        #LandlineForm,
        # show all phones in cases
        landline= Landline.objects.filter(customer=customer)
        landlines = []
        for l in landline:
            landlines.append({'form':LandlineForm(instance=l),
                            'landline':l})
        print(landlines)

        #WhatsAppForm
        # show all phones in cases
        whatsApp= WhatsApp.objects.filter(customer=customer)
        whatsApps = []
        for w in whatsApp:
            whatsApps.append({'form':WhatsAppForm(instance=w),
                            'number':w})
        print(whatsApps)

        #Addressfomr
        address = Address.objects.filter(customer=customer)
        addresses = []
        for a in address:
            addresses.append({'form':AddressForm(instance=a),
                            'adrs':a})
        print(addresses)



    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {
        'layout_path': layout_path,
        'customer': customer,
        'form': form,
        'phones':phones,
        'whatsApps':whatsApps,
        'landlines':landlines,
        'emails':emails,
        'addresses':addresses,
    }
    context = TemplateLayout.init(request, context)
    return render(request, "edit_customer.html", context)



