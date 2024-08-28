from datetime import datetime, timedelta
import io
from django.contrib.auth.decorators import login_required, user_passes_test
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper

from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from django.utils import timezone
from django.utils.timezone import make_aware

from apps.dashboard.models import (Advence, Booking, EmployeeAction, Inquiry, InquiryNotify,
    InquiryStatus, MessageNotify, Quotation, Request, Status, Country, InvoiceToSP)
from apps.dashboard.models_com import SuperProvider

import cloudinary
import cloudinary.uploader
from xhtml2pdf import pisa

@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['accountant','financial']).exists())
def invoices_list_view(request):

    title = 'Invoices list'

    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()
    messages = MessageNotify.objects.filter(employee=request.user.employee)
    messages_counter = messages.count()


    underproccess = Status.objects.get(name = 'underproccess')
    inquiries_s = InquiryStatus.objects.filter(status = underproccess )


    # Handle search form submission
    if request.method == 'GET':
        # Get the name entered in the query parameter
        last_3m = request.GET.get('3m')
        sp_last_m = request.GET.get('last_month')
        sp_this_m = request.GET.get('this_month')

        if last_3m:
            now = make_aware(datetime.now())
            period = 30*int(last_3m)
            start_date = now - timedelta(days=period)
            inquiries_s = inquiries_s.filter(update__range=[start_date, now])

        if sp_last_m:

            end_date = make_aware(datetime.now()) - timedelta(days=30)
            start_date = end_date - timedelta(days=30)
            inquiries_s = inquiries_s.filter(update__range=[start_date, end_date])

            if sp_last_m != "all":
                sp = SuperProvider.objects.get(id=sp_last_m)
                inquiries_s = inquiries_s.filter(inquiry__sp = sp)

        if sp_this_m:

            now = make_aware(datetime.now())
            start_date = now - timedelta(days=30)
            inquiries_s = inquiries_s.filter(update__range=[start_date, now])
            
            if sp_this_m != "all":
                sp = SuperProvider.objects.get(id=sp_this_m)
                inquiries_s = inquiries_s.filter(inquiry__sp = sp)

        

    inquiries = []
    for i in inquiries_s:
        inquiries.append(i.inquiry)
    #inquiries = inquiries_s.values_list('inquiry', flat=True)


    search_counter = len(inquiries)

    

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(inquiries, 40)  # Show 40 customers per page

    try:
        inquiries = paginator.page(page)
    except PageNotAnInteger:
        inquiries = paginator.page(1)
    except EmptyPage:
        inquiries = paginator.page(paginator.num_pages)

    
    inquiry = []
    for i in inquiries:
        try:
            advence = Advence.objects.get(inquiry=i)
        except :
            advence = 0

        try:
            # Assuming 'i' is the specific inquiry instance
            quotations = Quotation.objects.filter(inquiry=i)
            totale = 0
            for q in quotations:
                totale = totale + float(q.total)
        except:
            totale = 0
            
        reqs = Request.objects.filter(inquiry=i) 

        try:
            stt = InquiryStatus.objects.get(inquiry=i)
            act = EmployeeAction.objects.filter(inquiry=i).last()
            

            newDelay = stt.newDelay 
            connectDelay = stt.connectDelay 
            underproccessDelay = stt.underproccessDelay 
            sendqDelay = stt.sendqDelay 
            pendingDelay = stt.pendingDelay 
            sendbDelay = stt.sendbDelay 
            doneDelay = stt.doneDelay
            cancelDelay = stt.cancelDelay


            new_connect = (connectDelay - newDelay) if newDelay is not None and connectDelay is not None and connectDelay > newDelay else '_'
            connect_sendqDelay = (sendqDelay - connectDelay) if sendqDelay is not None and connectDelay is not None and sendqDelay > connectDelay else '_'
            sendqDelay_underproccessDelay = (underproccessDelay - sendqDelay) if underproccessDelay is not None and sendqDelay is not None and underproccessDelay > sendqDelay else '_'
            underproccessDelay_sendbDelay = (sendbDelay - underproccessDelay) if sendbDelay is not None and underproccessDelay is not None and sendbDelay > underproccessDelay else '_'
            
            sendqDelay_pendingDelay = (pendingDelay - sendqDelay) if sendqDelay is not None and pendingDelay is not None and pendingDelay > sendqDelay else '_'
            connect_underproccessDelay = (underproccessDelay - connectDelay) if underproccessDelay is not None and connectDelay is not None and underproccessDelay > connectDelay else '_'
            sendbDelay_doneDelay = (doneDelay - sendbDelay) if doneDelay is not None and sendbDelay is not None and doneDelay - sendbDelay else '_'

            
            inquiry.append({'info':i,
                            'state':stt,
                            'advence' : advence,
                            'totale':totale,
                            'action':act,
                            'requests':reqs,
                            
                            'connect_sendqDelay': connect_sendqDelay,
                            'new_connect': new_connect,
                            'sendqDelay_underproccessDelay': sendqDelay_underproccessDelay,
                            'underproccessDelay_sendbDelay': underproccessDelay_sendbDelay,
                            'sendqDelay_pendingDelay': sendqDelay_pendingDelay,
                            'connect_underproccessDelay': connect_underproccessDelay,
                            'sendbDelay_doneDelay': sendbDelay_doneDelay,

                        })
        except:
            inquiry.append({'info':i,
                        })

    try:
        cols = request.user.employee.columns.split("*,*")
    except:
        cols = "all"

    

    # Handle search form submission
    if request.method == 'GET':
        emp_name = request.GET.get('emp_name')
        print(emp_name)

        if emp_name:
            employees = employees.filter(first_name__icontains=emp_name)
        

        # If it's an AJAX request, return a JSON response
        if request.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            # Return a JSON response with the employee data
            return JsonResponse({'employees': [{'id': emp.user.id, 'first_name': emp.first_name, 'last_name': emp.last_name, 'email': emp.email, 'phone_number': emp.phone_number, 'position': emp.position.name} for emp in employees]})


    print(inquiry)

    sps = SuperProvider.objects.all()

    # Render the initial page with the full customer list
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'position': request.user.employee.position,
            'layout_path': layout_path,
            'inquiries': inquiries,
            'inquiries_with_pages': inquiries,
            'inquiries': inquiry,
            'notifications':notifications,
            'notifications_counter':notifications_counter,
            "search_counter":search_counter,
            "states":Status.objects.all(),
            'messages':messages,
            'messages_counter':messages_counter,
            'sps' : sps,
            "cols":cols,
            
            }
    

    context = TemplateLayout.init(request, context)

    return render(request, 'accountant/list.html',context)

@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['financial']).exists())
def invioces_report_view(request):

    underproccess = Status.objects.get(name = 'underproccess')
    inquiries_s = InquiryStatus.objects.filter(status = underproccess )


    if request.method == 'GET':
        # Get the name entered in the query parameter
        last_3m = request.GET.get('3m')
        sp_last_m = request.GET.get('last_month')
        sp_this_m = request.GET.get('this_month')

        title = "invoices - "

        if last_3m:
            title += f"last {last_3m} month"
            now = make_aware(datetime.now())
            period = 30*int(last_3m)
            start_date = now - timedelta(days=period)
            inquiries_s = inquiries_s.filter(update__range=[start_date, now])

        if sp_last_m:

            end_date = make_aware(datetime.now()) - timedelta(days=30)
            start_date = end_date - timedelta(days=30)
            inquiries_s = inquiries_s.filter(update__range=[start_date, end_date])

            if sp_last_m != "all":
                sp = SuperProvider.objects.get(id=sp_last_m)
                inquiries_s = inquiries_s.filter(inquiry__sp = sp)
                title += f"for {sp.name} in last month"
            else :
                title += "all sp in last month"

        if sp_this_m:

            now = make_aware(datetime.now())
            start_date = now - timedelta(days=30)
            inquiries_s = inquiries_s.filter(update__range=[start_date, now])
            
            if sp_this_m != "all":
                sp = SuperProvider.objects.get(id=sp_this_m)
                inquiries_s = inquiries_s.filter(inquiry__sp = sp)
                title += f"for {sp.name} in this month"
            else :
                title += "all sp in this month"

        

    total = 0
    inquiries = []
    for i in inquiries_s:
        inquiries.append(i.inquiry)
    #inquiries = inquiries_s.values_list('inquiry', flat=True)

    search_counter = len(inquiries)

    
    inquiry = []
    for i in inquiries:
        try:
            advence = Advence.objects.get(inquiry=i)
        except :
            advence = 0

        try:
            # Assuming 'i' is the specific inquiry instance
            quotations = Quotation.objects.filter(inquiry=i)
            totale = 0
            for q in quotations:
                totale = totale + float(q.total)
                reference = q.invoice_counter
        except:
            totale = 0


        cCode = request.country_code_prefix.replace("/", "").replace("\\", "")
        print(cCode)
        try:
            country = Country.objects.get(abr=cCode)
        except:
            country = Country.objects.get(abr="AE")
        vat = country.vat
        total_with_vat = totale + (totale * vat)
        total+=total_with_vat


        reqs = Request.objects.filter(inquiry=i) 

        try:
            stt = InquiryStatus.objects.get(inquiry=i)
            act = EmployeeAction.objects.filter(inquiry=i).last()
            

            newDelay = stt.newDelay 
            connectDelay = stt.connectDelay 
            underproccessDelay = stt.underproccessDelay 
            sendqDelay = stt.sendqDelay 
            pendingDelay = stt.pendingDelay 
            sendbDelay = stt.sendbDelay 
            doneDelay = stt.doneDelay
            cancelDelay = stt.cancelDelay


            new_connect = (connectDelay - newDelay) if newDelay is not None and connectDelay is not None and connectDelay > newDelay else '_'
            connect_sendqDelay = (sendqDelay - connectDelay) if sendqDelay is not None and connectDelay is not None and sendqDelay > connectDelay else '_'
            sendqDelay_underproccessDelay = (underproccessDelay - sendqDelay) if underproccessDelay is not None and sendqDelay is not None and underproccessDelay > sendqDelay else '_'
            underproccessDelay_sendbDelay = (sendbDelay - underproccessDelay) if sendbDelay is not None and underproccessDelay is not None and sendbDelay > underproccessDelay else '_'
            
            sendqDelay_pendingDelay = (pendingDelay - sendqDelay) if sendqDelay is not None and pendingDelay is not None and pendingDelay > sendqDelay else '_'
            connect_underproccessDelay = (underproccessDelay - connectDelay) if underproccessDelay is not None and connectDelay is not None and underproccessDelay > connectDelay else '_'
            sendbDelay_doneDelay = (doneDelay - sendbDelay) if doneDelay is not None and sendbDelay is not None and doneDelay - sendbDelay else '_'

            try:
                booking = Booking.objects.get(inquiry = i)
            except:
                booking = None

            inquiry.append({'info':i,
                            'state':stt,
                            'advence' : advence,
                            'totale':totale,
                            'action':act,
                            'requests':reqs,
                            'booking':booking,
                            'total_with_vat':total_with_vat,
                            'reference':reference,
                            
                            'connect_sendqDelay': connect_sendqDelay,
                            'new_connect': new_connect,
                            'sendqDelay_underproccessDelay': sendqDelay_underproccessDelay,
                            'underproccessDelay_sendbDelay': underproccessDelay_sendbDelay,
                            'sendqDelay_pendingDelay': sendqDelay_pendingDelay,
                            'connect_underproccessDelay': connect_underproccessDelay,
                            'sendbDelay_doneDelay': sendbDelay_doneDelay,

                        })
        except:
            inquiry.append({'info':i,
                        })
    

    # Create a PDF template using Django template
    template_path = 'accountant/export.html'  # Create a template for your PDF
    template = get_template(template_path)

    context = {
                "inquiries":inquiry,
                "title":title,
                "total":total,
                }
    
    html_content = template.render(context)

    # Create a PDF file using ReportLab
    pdf_file = io.BytesIO()
    pisa.CreatePDF(html_content, dest=pdf_file)

    # Set response content type
    response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')

    # Set the filename for download
    response['Content-Disposition'] = f'inline; filename="{title}.pdf"'

    return response



@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['financial']).exists())
def invioces_to_sp_table(request):
    title = 'Invoice To SP Table'

    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()
    messages = MessageNotify.objects.filter(employee=request.user.employee)
    messages_counter = messages.count()



    # Render the initial page with the full customer list
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'position': request.user.employee.position,
            'layout_path': layout_path,
            'title': title,
            'notifications':notifications,
            'notifications_counter':notifications_counter,
            "states":Status.objects.all(),
            'messages':messages,
            'messages_counter':messages_counter,
            'invoicesToSPs':InvoiceToSP.objects.all(),


            
            }
    

    context = TemplateLayout.init(request, context)

    return render(request, 'accountant/invoiceToSPTable.html',context)
@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['financial']).exists())
def invioces_to_sp_form(request):

    title = 'Invoice To SP Form'

    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()
    messages = MessageNotify.objects.filter(employee=request.user.employee)
    messages_counter = messages.count()

    sps = SuperProvider.objects.all()
    cCode = request.country_code_prefix.replace("/", "").replace("\\", "")
    print(cCode)
    try:
        country = Country.objects.get(abr=cCode)
    except:
        country = Country.objects.get(abr="AE")
    vat = country.vat

    marketingPer = 5

    if request.method == 'POST':
        date = request.POST.get('date')
        sp = request.POST.get('sp')
        total = float(request.POST.get('total'))
        pricingMarketing = float(request.POST.get('pricingMarketing'))
        email = request.POST.get('email')

        try:
            invoices_pdf = request.FILES.get('invoices_pdf')
            # Upload images to Cloudinary
            cloudinary_response = cloudinary.uploader.upload(invoices_pdf)
            invoices_pdf_url = cloudinary_response['secure_url']
        except:
            invoices_pdf_url = ""

        try:
            marketing_pdf = request.FILES.get('marketing_pdf')
            # Upload images to Cloudinary
            cloudinary_response = cloudinary.uploader.upload(marketing_pdf)
            marketing_pdf_url = cloudinary_response['secure_url']
        except:
            marketing_pdf_url = ""

        sp = SuperProvider.objects.get(id = sp)

        totnovat =  total - (total * (marketingPer/100))
        totvat = totnovat - (totnovat * (vat / 100))

        tosp = InvoiceToSP.objects.create(
            sp = sp,
            date = date,
            total = total,
            totalwithoutvat = totnovat,
            vat = vat,
            totalwithvat = totvat,
            Marketing_price = pricingMarketing ,
            email = email,
            invoices_pdf_url = invoices_pdf_url,
            marketing_pdf_url = marketing_pdf_url,
        )
    
        return redirect('invoices_list')




    # Render the initial page with the full customer list
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})
    context = {'position': request.user.employee.position,
            'layout_path': layout_path,
            'title': title,
            'notifications':notifications,
            'notifications_counter':notifications_counter,
            "states":Status.objects.all(),
            'messages':messages,
            'messages_counter':messages_counter,
            'sps' : sps,
            'vat' : vat,
            'marketingPer' : marketingPer,

            
            }
    

    context = TemplateLayout.init(request, context)

    return render(request, 'accountant/invoiceToSPFrom.html',context)