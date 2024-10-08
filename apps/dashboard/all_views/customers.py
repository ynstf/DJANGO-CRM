import apps.dashboard.models_com
import django.urls
from django.urls import reverse
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from apps.authentication.models import Employee, Permission, Position
from django.shortcuts import render, redirect, get_object_or_404
from apps.dashboard.models import Address, Customer, Inquiry, Language, Quotation, Service, Source, SuperProvider
from ..forms import CustomerForm, AddressForm, InquiryForm,CustomerFormEdit
from apps.dashboard.models import PhoneNumber, Email, Landline, WhatsApp, Emirate, Request
from ..forms import PhoneNumberForm, EmailForm, LandlineForm, WhatsAppForm
from ..models import Country,Customer, Nationality, InquiryNotify, Status, InquiryStatus, IsEmployeeNotified, InquiryReminder
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from ..models import Email,PhoneNumber,WhatsApp,Landline
import json
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.utils import timezone
import cloudinary
import cloudinary.uploader

######### permissions #########
"""
customer list
add customer
see customer info
edit customer
"""

############### customer manupilations #################
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['call_center', 'admin']).exists() or (Permission.objects.get(name="customer list") in u.employee.permissions.all()))
def customer_list_view(request):
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

        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        print(start_date,end_date)

        #email = request.GET.get('email')
        search_fields = []
        # Filter customers based on the entered name
        if name_query:
            search_fields.append({'name':'name',
                                'value':name_query})
            customers = customers.filter(first_name__icontains=name_query)
        
        if id_query:
            search_fields.append({'name':'id',
                                'value':id_query})
            customers = customers.filter(id=id_query)

        if trn_query:
            search_fields.append({'name':'trn',
                                'value':trn_query})
            customers = customers.filter(trn__icontains=trn_query)

        if start_date and end_date:
            search_fields.append({'name': 'date', 'start_date': start_date, "end_date":end_date })
            customers = customers.filter(register__range=[start_date, end_date])

        if add_name_query:
            search_fields.append({'name':'add_name',
                                'value':add_name_query})
            customers = customers.filter(address__address_name__icontains=add_name_query)

        if language_query:
            search_fields.append({'name':'language',
                                'value':language_query})
            id = Language.objects.get(name=language_query)
            customers = customers.filter(language=id)

        if nationality_query:
            search_fields.append({'name':'nationality',
                                'value':nationality_query})
            id = Nationality.objects.get(name=nationality_query)
            customers = customers.filter(nationality=id)

        if source_query:
            search_fields.append({'name':'source',
                                'value':source_query})
            id = Source.objects.get(name=source_query)
            customers = customers.filter(inquiry__source=id)
            
        # Order the customers from newest to oldest based on registration date
        customers = customers.order_by('-register')

        search_counter = customers.count()

        if number_query:
            search_fields.append({'name':'number',
                                'value':number_query})
            phones = PhoneNumber.objects.all()
            phones = phones.filter(number__icontains=number_query)
            customers = [phone.customer for phone in phones ]


        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(customers, 40)  # Show 40 customers per page

        try:
            customers = paginator.page(page)
        except PageNotAnInteger:
            customers = paginator.page(1)
        except EmptyPage:
            customers = paginator.page(paginator.num_pages)

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
    #statu = InquiryStatus.objects.get(inquiry=Inquiry.objects.filter(customer=c).first()).status
    for c in customers:
        try:
            customer.append({'info':c,
                            'number':PhoneNumber.objects.filter(customer=c).first(),
                            'email':Email.objects.filter(customer=c).first(),
                            'source':Inquiry.objects.filter(customer=c).first().source,
                            'inquiries':Inquiry.objects.filter(customer=c),
                            'statu':InquiryStatus.objects.get(inquiry=Inquiry.objects.filter(customer=c).last()).status
                        })
        except:
            customer.append({'info':c,
                            'number':PhoneNumber.objects.filter(customer=c).first(),
                            'email':Email.objects.filter(customer=c).first(),
                            'source':"None",
                            'inquiries':Inquiry.objects.filter(customer=c)
                        })
            

    # all language
    languages = Language.objects.all()
    nationality = Nationality.objects.all()
    sources = Source.objects.all()

    context = {'position': request.user.employee.position,
                'layout_path': layout_path,
                'customers': customer,
                "customers_with_pages":customers,
                "search_counter":search_counter,

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

                'search_fields':search_fields,

                }
    

    context = TemplateLayout.init(request, context)
    return render(request, 'customer/customer_list.html', context)



@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['call_center', 'admin']).exists() or (Permission.objects.get(name="add customer") in u.employee.permissions.all()))
def add_customer_view(request):
    
    if request.method == 'POST':
        #customer fields
        customer_form = CustomerForm(request.POST, prefix='customer')

        #contact fields
        phone_form = request.POST.getlist('customer-phone_numbers')
        whatsapp_form = request.POST.getlist('customer-whats_apps')
        landline_form = request.POST.getlist('customer-landlines')
        email_form = request.POST.getlist('customer-emails')
        merge_option = request.POST.get('merge_option')
        merge = merge_option == 'yes'


        #address fields
        adress_name = request.POST.getlist('address-address_name')
        adress_type = request.POST.getlist('address-type')
        emarate = request.POST.getlist('address-emirate')
        adress_desc = request.POST.getlist('address-description_location')
        location = request.POST.getlist('address-location')

        #inquiry fields
        inq_date = request.POST.getlist('inquiry-date_inq')
        inq_source = request.POST.getlist('customer-source')
        inq_service = request.POST.getlist('inquiry-services')
        sp = request.POST.getlist('inquiry-superprovider')

        remainder_checked = request.POST.getlist('remainder_check')
        schedule_time = request.POST.getlist('inquiry-reminder')


        inq_desc = request.POST.getlist('inquiry-description')

        # counter to know inquiries of each address
        inq_counters = request.POST.get('inq_counters')

        


        user_already_exist = False
        common_element = set(phone_form) & set(list(PhoneNumber.objects.values_list('number',flat=True)))
        if common_element and '+971' not in set(phone_form) :
            phone = list(common_element)[0]
            print('already exist :',phone)
            customer = PhoneNumber.objects.get(number = phone).customer
            user_already_exist = True
            print(customer.first_name)
        else:
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


        print(inq_counters)
        print(adress_name,adress_type,emarate,adress_desc,location)
        print(inq_date,inq_source,inq_service,inq_desc)

        # Iterate through the data and create Address instances
        
        
        addresses = []
        for i in range(len(adress_name)):

            try:
                coords = location[i].split(",")
                latitude = coords[0]
                longitude = coords[1]
            except:
                latitude = 0
                longitude = 0

            google_maps_link = f"https://www.google.com/maps?q={latitude},{longitude}"

            if emarate[i] and adress_type[i] :
                address = Address(
                    customer=customer,
                    address_name=adress_name[i],
                    type=adress_type[i],
                    emirate=Emirate.objects.get(id=emarate[i]),  # Replace with the actual Emirate retrieval
                    description_location=adress_desc[i],
                    location=location[i],
                    location_url=google_maps_link,
                )
                address.save()
                addresses.append(address)
            else:
                if emarate[i]=="" and adress_type[i]=="" :
                    address = Address(
                    customer=customer,
                    address_name=adress_name[i],
                    description_location=adress_desc[i],
                    location=location[i],
                    location_url=google_maps_link,
                    )
                    address.save()
                    addresses.append(address)
                else:
                    if emarate[i]=="":
                        address = Address(
                            customer=customer,
                            address_name=adress_name[i],
                            type=adress_type[i],
                            description_location=adress_desc[i],
                            location=location[i],
                            location_url=google_maps_link,
                        )
                        address.save()
                        addresses.append(address)

                    if adress_type[i]=="" :
                        address = Address(
                            customer=customer,
                            address_name=adress_name[i],
                            emirate=Emirate.objects.get(id=emarate[i]),  # Replace with the actual Emirate retrieval
                            description_location=adress_desc[i],
                            location=location[i],
                            location_url=google_maps_link,
                        )
                    
                        address.save()
                        addresses.append(address)

        if inq_counters :
            q=0
            s = json.loads(inq_counters)
            for i in range(1,len(s)+1):
                try:
                    print('dkheeeeeeeeeeeeeelt')
                    for inq_per_address in range(s[f"{i}"]):
                        remainder_checked = request.POST.get(f'remainder_check_{i}_{inq_per_address+1}')

                        print("q : ",q)
                        print("s : ",s)
                        print("i : ",i,)
                        print("inq_per_address :",inq_per_address)
                        print("remainder_checked :",remainder_checked)

                        inq_employees = request.POST.getlist(f'inquiry-employees_{i}_{inq_per_address+1}')
                        address = addresses[i-1]
                        services_set = Service.objects.get(name=inq_service[q])
                        current_inq_source_id = inq_source[q]
                        current_inq_source = Source.objects.get(id=current_inq_source_id)
                        current_sp = SuperProvider.objects.get(id=sp[q])

                        print("customer :",customer)
                        print("address :",address)
                        print("source :",current_inq_source)
                        print("services :",services_set)
                        print("sp :",current_sp)
                        print("description :",inq_desc[q])

                        inquiry = Inquiry(
                            customer=customer,
                            address=address,
                            source = current_inq_source,
                            services=services_set,
                            sp=current_sp,
                            description=inq_desc[q],
                            
                        )
                        inquiry.save()

                        # upload images 
                        if request.method == 'POST':
                            try:
                                imgs = request.FILES.getlist(f'images_{i}_{inq_per_address+1}')
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
                        print("1")

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

                        print("2")
                        inquiry.save()


                        print("3")
                        new = Status.objects.get(name = "new")
                        inq_state = InquiryStatus(
                            inquiry = inquiry,
                            status= new
                        )
                        inq_state.newDelay = timezone.now()
                        inq_state.save()

                        print("4")

                        req = Request(
                            inquiry = inquiry,
                            demande = "by call center"
                        )
                        req.save()
                        print("5")
                        
                        if remainder_checked == "on":
                            print("waaaaaaaaaaaaaaaaaaaa rani dkhjaaaalt")
                            employee_id = request.user.employee.id
                            employee = Employee.objects.get(id=employee_id)
                            reminder = InquiryReminder(
                                employee = employee,
                                inquiry=inquiry,
                                service=services_set,
                                gool='inquiry',
                                schedule=schedule_time[q]
                            )
                            reminder.save()
                        print("6")
                        q+=1

                except:
                    pass


        if merge:
            messages.success(request, "The two customers have been successfully merged.")
            return redirect("customer_info", id=customer.id)
        else :
            if merge=="no":
                messages.info(request, "The merge operation has been canceled.")
            return redirect('customer_list')
        
    
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

    all_sp = SuperProvider.objects.all()

    cCode = request.country_code_prefix.replace("/", "").replace("\\", "")
    print(cCode)

    try:
        country = Country.objects.get(abr=cCode)
    except:
        country = Country.objects.get(abr="AE")

    numberPrefix = country.numberPrefix


    # Set the layout path even when authentication fails
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'position': request.user.employee.position,
                'layout_path': layout_path,
                'customer_form': customer_form, 
                'inquiry_form':inquiry_form,

                'Sources':Sources,
                'Genders':Genders,
                'Nationalities':Nationalities,
                'Services':Services,
                'Languages':Languages,
                'Emirates':Emirates,
                'types':types,
                'all_sp':all_sp,
                'team_leaders':Employee.objects.filter(position=Position.objects.get(name='team leader')),

                'numberPrefix':numberPrefix,
                }
    
    context = TemplateLayout.init(request, context)
    return render(request, 'customer/add_customer.html', context)

def merge_customer(request, id):
    if request.method == 'POST':
        action = request.POST.get('action')
        addresses = request.POST.getlist('addresses')

        if action == 'merge':

            messages.success(request, "The two customers have been successfully merged.")
        elif action == 'cancel':
            # delete addresse
            for adr in addresses:
                address = Address.objects.get(id=adr)
                address.delete()

            messages.info(request, "The merge operation has been canceled.")
        return redirect("customer_info", id=id)
    else:
        # Handle GET request if needed
        return redirect("customer_list")

@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['call_center', 'admin']).exists() or (Permission.objects.get(name="see customer info") in u.employee.permissions.all()) )
def customer_info_view(request, id):
    customer = get_object_or_404(Customer, id=id)
    addresses = Address.objects.filter(customer=customer)
    inquiries = Inquiry.objects.filter(address__in=addresses)

    # Add a boolean field indicating if there are any quotations for each inquiry
    for inquiry in inquiries:
        inquiry.has_quotations = Quotation.objects.filter(inquiry=inquiry).exists()



    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'position': request.user.employee.position,
            'layout_path': layout_path,
            'customer': customer,
            'addresses': addresses,
            'inquiries': inquiries,
            
            }
    context = TemplateLayout.init(request, context)
    return render(request, "customer/customer_info.html", context)

@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['call_center', 'admin']).exists() or (Permission.objects.get(name="edit customer") in u.employee.permissions.all()))
def edit_customer_view(request, id):
    customer = get_object_or_404(Customer, id=id)
    
    if request.method == 'POST':

        first_name = request.POST.get('customer-first_name')
        last_name = request.POST.get('customer-last_name')
        gender = request.POST.get('customer-gender')
        nationality_cus = request.POST.get('customer-nationality')
        
        language = request.POST.get('customer-language')
        trn = request.POST.get('customer-trn')
        
        #contact fields
        phone_form = request.POST.getlist('customer-phone_numbers')
        whatsapp_form = request.POST.getlist('customer-whats_apps')
        landline_form = request.POST.getlist('customer-landlines')
        email_form = request.POST.getlist('customer-emails')

        print(phone_form,whatsapp_form,landline_form,email_form)

        #address fields
        adress_name = request.POST.getlist('address-address_name')
        adress_type = request.POST.getlist('address-type')
        emarate = request.POST.getlist('address-emirate')
        adress_desc = request.POST.getlist('address-description_location')
        location = request.POST.getlist('address-location')


        #inquiry fields
        inq_id = request.POST.getlist('inquiry-id')
        inq_date = request.POST.getlist('inquiry-date_inq')
        inq_source = request.POST.getlist('customer-source')
        inq_service = request.POST.getlist('inquiry-services')
        inq_desc = request.POST.getlist('inquiry-description')
        inq_sp = request.POST.getlist('inquiry-superprovider')

        

        # counter to know inquiries of each address
        inq_counters = request.POST.get('inq_counters')


        # Save the customer
        customer = get_object_or_404(Customer, id=id)
        customer.employee = Employee.objects.get(user=request.user)
        customer.first_name = first_name
        customer.last_name = last_name
        customer.gender = gender

        print(nationality_cus)
        try:
            nat = Nationality.objects.get(id=nationality_cus)
            customer.nationality = nat
        except:
            pass
        
        try:
            lg = Language.objects.get(id=language)
            customer.language = lg
        except:
            pass

        customer.trn = trn

        customer.save()
        print(customer)

        # Save the emails
        pre_numbers = Email.objects.filter(customer=customer)
        pre_numbers.delete()
        for e in email_form:
            email = Email(customer=customer,email=e)
            email = email.save() 

        # Save the phones
        pre_numbers = PhoneNumber.objects.filter(customer=customer)
        pre_numbers.delete()
        for p in phone_form:
            phone = PhoneNumber(customer=customer,number=p)
            phone = phone.save()

        # Save the whatsapps
        pre_numbers = WhatsApp.objects.filter(customer=customer)
        pre_numbers.delete()
        for w in whatsapp_form:
            whatsapp = WhatsApp(customer=customer,whatsapp=w)
            whatsapp = whatsapp.save()

        # Save the landlines
        pre_numbers = Landline.objects.filter(customer=customer)
        pre_numbers.delete()
        for l in landline_form:
            landline = Landline(customer=customer,landline=l)
            landline = landline.save()

        
        # Iterate through the data and update Address instances
        address = Address.objects.filter(customer=customer)
        address.delete()
        addresses = []
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
                addresses.append(address)
            else:
                if emarate[i]=="" and adress_type[i]=="" :
                    address = Address(
                    customer=customer,
                    address_name=adress_name[i],
                    description_location=adress_desc[i],
                    location=location[i],
                    )
                    address.save()
                    addresses.append(address)
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
                        addresses.append(address)

                    if adress_type[i]=="" :
                        address = Address(
                            customer=customer,
                            address_name=adress_name[i],
                            emirate=Emirate.objects.get(id=emarate[i]),  # Replace with the actual Emirate retrieval
                            description_location=adress_desc[i],
                            location=location[i],
                        )
                        address.save()
                        addresses.append(address)
        

        # Iterate through the data and update Inquiry instances
        inqs = Inquiry.objects.filter(customer=customer)
        
        for i in Inquiry.objects.filter(customer=customer):
            InquiryNotify.objects.filter(inquiry=i).delete()
        
        #inqs.delete()

        q=0
        s = json.loads(inq_counters)
        print("debugging")
        print("counter")
        print(s)
        print("inquiries data")
        print(inq_date,inq_source,inq_service,inq_desc)
        print("inquiries id")
        print(inq_id)

        for i in range(1,len(s)+1):
            for _ in range(s[f"{i}"]):
                print(f'lenth of inquiries in adress{i}',s[f"{i}"])
                print("i: ",i)
                print("q: ",q)
                if s[f"{i}"]>0:
                    
                    print(adress_name[i-1])
                    address = addresses[i-1]
                    services_set = Service.objects.get(name=inq_service[q])
                    inq_src = Source.objects.get(id=inq_source[q])

                    print(inq_id[q])
                    if inq_id[q]!="new":
                        inq_employees = request.POST.getlist(f'inquiry-employees_{inq_id[q]}')
                        inquiry = Inquiry.objects.get(id=inq_id[q])

                        inquiry.customer = customer
                        inquiry.address = address
                        inquiry.source = inq_src
                        inquiry.description = inq_desc[q]
                        current_sp = SuperProvider.objects.get(id=inq_sp[q])
                        inquiry.sp = current_sp
                        inquiry.services = services_set

                        inquiry.save()

                        

                        new = Status.objects.get(name = "new")
                        inq_state = InquiryStatus.objects.get(inquiry = inquiry)
                        #inq_state.status = new


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
                        
                        q+=1
                    else:
                        inquiry = Inquiry(
                            customer=customer,
                            address = address,
                            source = inq_src,
                            description = inq_desc[q],
                            services = services_set
                        )

                        inquiry.save()

                        new = Status.objects.get(name = "new")
                        inq_state = InquiryStatus(inquiry = inquiry,status=new)
                        inq_state.save()
                        #inq_state.status = new


                        all_employees = Employee.objects.filter(sp_service=services_set)
                        for employee in all_employees:
                            notification = InquiryNotify(
                                employee = employee,
                                inquiry = inquiry,
                                service = services_set,
                                action = "new"
                            )
                            notification.save()

                            isnotify = IsEmployeeNotified(
                                employee = employee,
                                notified = False
                            )
                            isnotify.save()
                        q+=1
                else:
                    pass
                

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

        inquiry = Inquiry.objects.filter(customer=customer)
        inquiries = []
        for i in inquiry:
            inquiries.append({'form':InquiryForm(instance=i),
                            'inq':i})
        print(inquiries)
        
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
    inquiries = Inquiry.objects.all()
    all_sp = SuperProvider.objects.all()

    #counters = {"""i want to include my counters of addresses and inquiries eg:{"1":1,"2":2} that mean i have the first address contain one inquiry and the second contain 2 inquiries that counter i want to send it to the front end to start count from it i dont start from zero like in creation no, i want to intiat my variables based on this counter so i can update my info end retrive the new counter of my new form"""}
    # Get the initial counters for addresses and inquiries
    initial_inq_counters = {str(index + 1): address.inquiry_set.count() for index, address in enumerate(customer.address_set.all())}
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})

    context = {
        'position': request.user.employee.position,
        'layout_path': layout_path,
        'customer': customer,
        'Genders':Genders,
        'Nationalities':Nationalities,
        'Languages':Languages,
        'types':types,
        'Services':Services,
        'Sources':Sources,
        'Emirates':Emirates,


        'initial_inq_counters': initial_inq_counters,
        'addresseslen':len(addresses),

        'form': form,
        'phones':phones,
        'whatsApps':whatsApps,
        'landlines':landlines,
        'emails':emails,
        'addresses':addresses,
        'inquiries':inquiries,
        'all_sp':all_sp,
    }
    context = TemplateLayout.init(request, context)
    return render(request, "customer/edit_customer.html", context)

