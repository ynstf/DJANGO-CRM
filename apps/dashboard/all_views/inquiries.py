from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.template.loader import get_template
from web_project.template_helpers.theme import TemplateHelper
from web_project import TemplateLayout
from xhtml2pdf import pisa
import io
from ..models import Inquiry, Quotation, Customer, PhoneNumber, Email, Service
from apps.authentication.models import Employee,Permission
from apps.dashboard.models import Source,Language,Nationality


################# inquiries ###################

@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['provider', 'admin','team_leader']).exists())
def inquiries_list_view(request):
    inquiries = Inquiry.objects.all()

    # Handle search form submission
    if request.method == 'GET':
        # Get the name entered in the query parameter
        name_query = request.GET.get('name')
        id_query = request.GET.get('id')

        service_query = request.GET.get('service')

        #number_query = request.GET.get('number')
        language_query = request.GET.get('language')
        nationality_query = request.GET.get('nationality')
        source_query = request.GET.get('source')
        #date_query = request.GET.get('date')
        add_name_query = request.GET.get('add_name')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')


        search_fields = []

        if name_query:
            search_fields.append({'name':'name',
                                'value':name_query})
            inquiries = inquiries.filter(customer__first_name__icontains=name_query)
        
        if id_query:
            search_fields.append({'name':'id',
                                'value':id_query})
            inquiries = inquiries.filter(id=id_query)

        if start_date and end_date:
            search_fields.append({'name': 'date', 'start_date': start_date, "end_date":end_date })
            inquiries = inquiries.filter(date_inq__range=[start_date, end_date])

        if add_name_query:
            search_fields.append({'name':'add_name',
                                'value':add_name_query})
            inquiries = inquiries.filter(address__address_name__icontains=add_name_query)
        
        if service_query:
            search_fields.append({'name':'service',
                                'value':service_query})
            id = Service.objects.get(name=service_query)
            inquiries = inquiries.filter(services=id)

        if source_query:
            search_fields.append({'name':'source',
                                'value':source_query})
            id = Source.objects.get(name=source_query)
            inquiries = inquiries.filter(source=id)

        if language_query:
            search_fields.append({'name':'language',
                                'value':language_query})
            id = Language.objects.get(name=language_query)
            inquiries = inquiries.filter(customer__language=id)

        if nationality_query:
            search_fields.append({'name':'nationality',
                                'value':nationality_query})
            id = Nationality.objects.get(name=nationality_query)
            inquiries = inquiries.filter(customer__nationality=id)











    # Render the initial page with the full customer list
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})

    context = {'position': request.user.employee.position,
                'layout_path': layout_path,
                'inquiries': inquiries,

                'search_fields':search_fields,
                }
    

    context = TemplateLayout.init(request, context)
    return render(request, 'inquiry/inquiries_list.html',context)



@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['provider', 'admin', 'team_leader']).exists())
def inquiry_info_view(request, id):
    inquiry = Inquiry.objects.get(id=id)
    customer = inquiry.customer

    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'position': request.user.employee.position,
            'layout_path': layout_path,
            'customer': customer,
            'inquiry': inquiry,
            'quotations': Quotation.objects.filter(inquiry=Inquiry.objects.get(id=id)),

            }
    context = TemplateLayout.init(request, context)
    return render(request, "inquiry/inquiries_info.html", context)


@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['provider', 'admin']).exists())
def make_quotation_view(request, id):
    
    if request.method == 'POST':
        quotation_service = request.POST.get('quotation-service')
        quotation_date = request.POST.get('quotation-date')

        details = request.POST.getlist('quotation-detail')
        prices = request.POST.getlist('quotation-price')
        quantities = request.POST.getlist('quotation-quantity')


        inquiry = Inquiry.objects.get(id=id)
        customer_id = inquiry.customer.id
        customer = Customer.objects.get(id=customer_id)
        employee_id = request.user.employee.id
        employee = Employee.objects.get(id=employee_id)

        print(employee,inquiry,customer,quotation_service,quotation_date,details,prices,quantities)
        
        srv_id = quotation_service
        quotation_service = Service.objects.get(id=srv_id)

        for i in range(len(prices)):

            quotation = Quotation(
                employee=employee,
                customer=customer,
                inquiry=inquiry,
                quotation_service=quotation_service,
                quotation_date=quotation_date,
                detail=details[i],
                price=prices[i],
                quantity=quantities[i],
                total=float(prices[i])*float(quantities[i])
            )
            quotation.save()

        return redirect('inquiry_info', id=id)



    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'position': request.user.employee.position,
            'layout_path': layout_path,
            'customer': Inquiry.objects.get(id=id).customer,
            'inquiry': Inquiry.objects.get(id=id),
            'services':Service.objects.all(),
            }
    context = TemplateLayout.init(request, context)
    return render(request, "inquiry/make_quotation.html", context)

@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['provider', 'admin']).exists())
def edit_quotation_view(request,id):
    inquiry = Inquiry.objects.get(id = id)

    quotations = Quotation.objects.filter(inquiry=inquiry)

    if request.method == 'POST':
        quotation_service = request.POST.get('quotation-service')
        quotation_date = request.POST.get('quotation-date')

        details = request.POST.getlist('quotation-detail')
        prices = request.POST.getlist('quotation-price')
        quantities = request.POST.getlist('quotation-quantity')


        inquiry = Inquiry.objects.get(id=id)
        customer_id = inquiry.customer.id
        customer = Customer.objects.get(id=customer_id)
        employee_id = request.user.employee.id
        employee = Employee.objects.get(id=employee_id)

        print(employee,inquiry,customer,quotation_service,quotation_date,details,prices,quantities)
        
        srv_id = quotation_service
        quotation_service = Service.objects.get(id=srv_id)

        #delete old values
        quots = Quotation.objects.filter(inquiry=inquiry)
        quots.delete()
        #save the new values
        for i in range(len(prices)):
            quotation = Quotation(
                employee=employee,
                customer=customer,
                inquiry=inquiry,
                quotation_service=quotation_service,
                quotation_date=quotation_date,
                detail=details[i],
                price=prices[i],
                quantity=quantities[i],
                total=float(prices[i])*float(quantities[i])
            )
            quotation.save()

        return redirect('inquiry/inquiry_info', id=id)






    
    date=quotations[0].quotation_date
    service=quotations[0].quotation_service
    # Render the initial page with the full customer list
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})

    context = {'position': request.user.employee.position,
                'layout_path': layout_path,
                'inquiry': Inquiry.objects.get(id=id),
                'date':date,
                'service' : service,
                'quotations':quotations,
                'services':Service.objects.all(),
                }
    

    context = TemplateLayout.init(request, context)
    return render(request, 'inquiry/edit_quotation.html',context)


@login_required(login_url='/')
#@user_passes_test(lambda u: u.groups.filter(name__in=['admin']).exists())
@user_passes_test(lambda u: u.groups.filter(name__in=['admin']).exists() or (Permission.objects.get(name="extract quotations") in u.employee.permissions.all()))
def generate_pdf_view(request, id):
    # Retrieve the inquiry and associated quotations
    inquiry = Inquiry.objects.get(id=id)
    quotations = Quotation.objects.filter(inquiry=inquiry)
    customer = Customer.objects.get(id=inquiry.customer.id)
    phone = PhoneNumber.objects.filter(customer=customer)[0]
    email = Email.objects.filter(customer=customer)[0]
    address = inquiry.address.address_name

    total = 0
    for quotation in quotations:
        total += float(quotation.total)


    date=quotations[0].quotation_date
    service=quotations[0].quotation_service

    # Create a PDF template using Django template
    template_path = 'pdf_template.html'  # Create a template for your PDF
    template = get_template(template_path)
    context = {'inquiry': inquiry,
                'quotations': quotations,
                'date':date,
                'service':service,
                'phone':phone,
                'address':address,
                'email':email,
                'total':total,

                }
    html_content = template.render(context)

    # Create a PDF file using ReportLab
    pdf_file = io.BytesIO()
    pisa.CreatePDF(html_content, dest=pdf_file)

    # Set response content type
    response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')

    # Set the filename for download
    response['Content-Disposition'] = f'inline; filename="{inquiry.customer.first_name}_{inquiry.customer.last_name}_quotation{inquiry.id}.pdf"'

    return response



