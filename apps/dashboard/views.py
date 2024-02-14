from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from apps.authentication.models import Employee
from django.shortcuts import render, redirect

from apps.dashboard.models import Address, Customer, Inquiry, Language, Service, Source
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

@login_required(login_url='/')
def dashboard(request):
    context={
    }
    context = TemplateLayout.init(request, context)
    return render(request, 'dashboard.html',context)

@login_required(login_url='/')
def customer_list(request):
    customers = Customer.objects.all()
    
    # Handle search form submission
    if request.method == 'GET':
        # Get the name entered in the query parameter
        name_query = request.GET.get('name')
        id_query = request.GET.get('id')
        trn_query = request.GET.get('trn')
        number_query = request.GET.get('number')
        language_query = request.GET.get('language')
        nationality_query = request.GET.get('nationality')
        source_query = request.GET.get('source')
        date_query = request.GET.get('date')
        add_name_query = request.GET.get('add_name')

        #email = request.GET.get('email')

        # Filter customers based on the entered name
        if name_query:
            customers = customers.filter(first_name__icontains=name_query)
        
        if id_query:
            customers = customers.filter(id=id_query)

        if trn_query:
            customers = customers.filter(trn__icontains=trn_query)

        if date_query:
            customers = customers.filter(register__icontains=date_query)

        if add_name_query:
            customers = customers.filter(address__address_name__icontains=add_name_query)

        if language_query:
            id = Language.objects.get(name=language_query)
            customers = customers.filter(language=id)

        if nationality_query:
            id = Nationality.objects.get(name=nationality_query)
            customers = customers.filter(nationality=id)

        if source_query:
            id = Source.objects.get(name=source_query)
            customers = customers.filter(source=id)




        if number_query:
            phones = PhoneNumber.objects.all()
            phones = phones.filter(number__icontains=number_query)
            customers = [phone.customer for phone in phones ]


        # If it's an AJAX request, return a JSON response
        if request.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            # show all detail
            customer = []
            for c in customers:
                customer.append({'info':c,
                    'number':PhoneNumber.objects.filter(customer=c).first(),
                    'email':Email.objects.filter(customer=c).first(),
                    })

            # Return a JSON response with the customer data
            return JsonResponse({'customers':customer })

    # Render the initial page with the full customer list
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})

    # show all infos
    customer = []
    for c in customers:
        customer.append({'info':c,
                        'number':PhoneNumber.objects.filter(customer=c).first(),
                        'email':Email.objects.filter(customer=c).first(),
                        })

    # all language
    languages = Language.objects.all()
    nationality = Nationality.objects.all()
    sources = Source.objects.all()

    context = {'layout_path': layout_path,
                'customers': customer,

                'name_query':name_query if name_query!=None else '' ,
                'id_query':id_query if id_query!=None else '' ,
                'trn_query':trn_query if trn_query!=None else '' ,
                'number_query':number_query if number_query!=None else '' ,
                'language_query':language_query if language_query!=None else '' ,
                'nationality_query':nationality_query if nationality_query!=None else '' ,
                'source_query':source_query if source_query!=None else '' ,
                'date_query':date_query if date_query!=None else '' ,
                'add_name_query':add_name_query if add_name_query!=None else '',

                'languages':languages ,
                'nationality':nationality,
                'sources':sources,

                }
    

    context = TemplateLayout.init(request, context)
    return render(request, 'customer_list.html', context)

@login_required(login_url='/')
def add_customer(request):
    if request.method == 'POST':
        #customer fields
        customer_form = CustomerForm(request.POST, prefix='customer')
        
        #contact fields
        phone_form = request.POST.getlist('customer-phone_numbers')
        whatsapp_form = request.POST.getlist('customer-whats_apps')
        landline_form = request.POST.getlist('customer-landlines')
        email_form = request.POST.getlist('customer-emails')

        #address fields
        adress_name = request.POST.getlist('address-address_name')
        adress_type = request.POST.getlist('address-type')
        emarate = request.POST.getlist('address-emirate')
        adress_desc = request.POST.getlist('address-description_location')
        location = request.POST.getlist('address-location')

        #inquiry fields
        inq_address = request.POST.getlist('inq_address')
        inq_date = request.POST.getlist('inquiry-date_inq')
        inq_time = request.POST.getlist('inquiry-time_inq')
        inq_number = request.POST.getlist('inquiry-inq_num')
        inq_service = request.POST.getlist('inquiry-services')
        inq_desc = request.POST.getlist('inquiry-description')


        # Assuming addressCounter is the total number of address forms submitted
        inqCounter = int(request.POST.get('inqCounter', 0))

        for i in range(1, inqCounter + 1):

            #inquiry fields
            inq_address = request.POST.getlist('inq_address-{i}')
            inq_date = request.POST.getlist('inquiry-date_inq-{i}')
            inq_time = request.POST.getlist('inquiry-time_inq-{i}')
            inq_number = request.POST.getlist('inquiry-inq_num-{i}')
            inq_service = request.POST.getlist('inquiry-services-{i}')
            inq_desc = request.POST.getlist('inquiry-description-{i}')

            print(inqCounter,inq_address,inq_date,inq_time,inq_number,inq_service,inq_desc)

        # Save the customer
        customer = customer_form.save(commit=False)
        customer.employee = Employee.objects.get(user=request.user)
        customer.save()

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

        # Iterate through the data and create Address instances
        for i in range(len(adress_name)):
            if emarate[i] and adress_type[i] :
                address = Address(
                    customer=customer,
                    address_name=adress_name[i],
                    type=adress_type[i],
                    emirate=Emirate.objects.get(id=emarate[i]),  # Replace with the actual Emirate retrieval
                    description_location=adress_desc[i],
                    location=location[i],
                )
                address.save()
            else:
                if emarate[i]=="" and adress_type[i]=="" :
                    address = Address(
                    customer=customer,
                    address_name=adress_name[i],
                    description_location=adress_desc[i],
                    location=location[i],
                )
                    address.save()
                
                else:
                    if emarate[i]=="":
                        address = Address(
                            customer=customer,
                            address_name=adress_name[i],
                            type=adress_type[i],
                            description_location=adress_desc[i],
                            location=location[i],
                        )
                        address.save()

                    if adress_type[i]=="" :
                        address = Address(
                            customer=customer,
                            address_name=adress_name[i],
                            emirate=Emirate.objects.get(id=emarate[i]),  # Replace with the actual Emirate retrieval
                            description_location=adress_desc[i],
                            location=location[i],
                        )
                        address.save()
            


        return redirect('customer_list')  # Redirect to the customer list page
    else:
        # Creating instances of forms with prefixes
        customer_form = CustomerForm(prefix='customer')
        inquiry_form = InquiryForm(prefix='inquiry')

        # You can set default values for some fields if needed
        # For example, get the first nationality from the database
        default_nationality = Nationality.objects.first()
        if default_nationality:
            customer_form.fields['nationality'].initial = default_nationality

        # Similarly, set default values for other fields as needed
            
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

    # Set the layout path even when authentication fails
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'layout_path': layout_path,
                'customer_form': customer_form, 
                'inquiry_form':inquiry_form,

                'Sources':Sources,
                'Genders':Genders,
                'Nationalities':Nationalities,
                'Services':Services,
                'Languages':Languages,
                'Emirates':Emirates,
                'types':types,

                }
    
    context = TemplateLayout.init(request, context)
    return render(request, 'add_customer.html', context)

@login_required(login_url='/')
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



@login_required(login_url='/')
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
