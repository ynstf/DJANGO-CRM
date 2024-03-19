from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.loader import get_template
from web_project.template_helpers.theme import TemplateHelper
from web_project import TemplateLayout

from ..models import Inquiry, Quotation, QuotationForm, Customer, PhoneNumber, Email, Service, Booking
from apps.authentication.models import Employee,Permission
from apps.dashboard.models import (Inquiry, InquiryStatus, Language, 
                                Nationality, InquiryNotify,
                                Source, Status, EmployeeAction,
                                IsEmployeeNotified,InquiryReminder)
from django.http import HttpResponse
from xhtml2pdf import pisa
import io
from datetime import datetime, timedelta
from django.contrib import messages

def make_inq_underproccess(request,inq_id):
    underproccess = Status.objects.get(name = "underproccess")
    inquiry = Inquiry.objects.get(id = inq_id)
    inq_state = InquiryStatus.objects.get(inquiry = inquiry)
    inq_state.status = underproccess
    inq_state.save()
    all_employees = Employee.objects.filter(sp_service=inquiry.services)

    #create action
    action = EmployeeAction(
        from_employee=request.user.employee,
        inquiry = inquiry,
        status = InquiryStatus.objects.get(inquiry = inquiry).status
    )
    action.save()

    #craete notifications
    for employee in all_employees:
        notification = InquiryNotify(
            employee = employee,
            inquiry = inquiry,
            service = inquiry.services,
            action = "underproccess"
        )
        notification.save()

        isnotify = IsEmployeeNotified(
            employee = employee,
            notified = False
        )
        isnotify.save()
    return redirect('inquiries_list')


@login_required(login_url='/')
@user_passes_test(lambda u: u.groups.filter(name__in=['call_center', 'admin']).exists() or (Permission.objects.get(name="edit quotation") in u.employee.permissions.all()) )
def make_booking_view(request,id):
    notifications = InquiryNotify.objects.filter(employee=request.user.employee)
    notifications_counter = notifications.count()

    inquiry = Inquiry.objects.get(id = id)
    quotations = Quotation.objects.filter(inquiry=inquiry)

    if request.method == 'POST':

        quotation_service = request.POST.get('quotation-service')
        quotation_date = request.POST.get('quotation-date')
        booking_details = request.POST.get('booking-details')
        booking_number = request.POST.get('booking-number')
        ref_number = request.POST.get('ref-number')
        schedule_time = request.POST.get('schedule-time')


        inquiry = Inquiry.objects.get(id=id)
        customer_id = inquiry.customer.id
        customer = Customer.objects.get(id=customer_id)
        employee_id = request.user.employee.id
        employee = Employee.objects.get(id=employee_id)



        srv_id = inquiry.services.id
        quotation_service = Service.objects.get(id=srv_id)


        number = Booking.objects.filter(booking_number=booking_number)
        print(number)
        if number:
            messages.info(request, "The booking already exist.")
            return redirect('inquiry_info' ,id=id)
        else:

            booking = Booking(
                employee=employee,
                customer=customer,
                inquiry=inquiry,
                booking_service=quotation_service,
                booking_date=quotation_date,
                details = booking_details,
                booking_number=booking_number,
                ref_number=ref_number
            )
            booking.save()

            reminder = InquiryReminder(
                employee = employee,
                inquiry=inquiry,
                service=quotation_service,
                schedule=schedule_time
            )
            reminder.save()

        print()
        
        return redirect('make_inq_underproccess', inq_id=id)



    
    date=quotations[0].quotation_date
    service=quotations[0].quotation_service
    sp=quotations[0].quotation_sp

    # monthly reminnder
    reminder_time = service.reminder_time
    # Get today's date
    today = datetime.now()
    # Add 5 months to today's date
    scheduling = today + timedelta(days=reminder_time*30)

    quotations=[]
    for q in Quotation.objects.filter(inquiry=Inquiry.objects.get(id = id)):
        print(q.data)
        quotations.append([d for d in q.data.split(",*,")])

    cols = Inquiry.objects.get(id=id).services.columns
    cols_list = cols.split(',')

    defult_data = []
    details = []
    prices = []
    quantities = []
    for i in range(len(quotations)):
        details.append(quotations[i][0])
        prices.append(quotations[i][len(quotations[i])-2])
        quantities.append(quotations[i][len(quotations[i])-1])
    
    for i in range(len(quotations)):
        data = []
        for d in quotations[i][1:-2]:
            data.append(d)

        result = [{"column_name": col, "data": d} for col, d in zip(cols_list[1:-2], data)]

        defult_data.append(
            {"detail":details[i], "result":result, "columns":cols_list[1:-2], "price":prices[i], "quantity":quantities[i] , "total":float(prices[i])*float(quantities[i])}
        )
    
    # Render the initial page with the full customer list
    layout_path = TemplateHelper.set_layout("layout_blank.html", context={})

    context = {'position': request.user.employee.position,
                'layout_path': layout_path,
                'notifications':notifications,
                'notifications_counter':notifications_counter,
                'inquiry': Inquiry.objects.get(id=id),
                'date':date,
                'service' : service,
                'quotations':defult_data,
                'services':Service.objects.all(),
                'sp':sp,
                'scheduling':scheduling,
                'reminder_time':reminder_time,
                }
    
    context = TemplateLayout.init(request, context)
    return render(request, 'booking/make_booking.html',context)


def generate_invoice_view(request, id):
    # Retrieve the inquiry and associated quotations
    inquiry = Inquiry.objects.get(id=id)
    quotations = Quotation.objects.filter(inquiry=inquiry)
    customer = Customer.objects.get(id=inquiry.customer.id)
    phone = PhoneNumber.objects.filter(customer=customer)[0]
    email = Email.objects.filter(customer=customer)[0]
    address = inquiry.address

    total = 0
    for quotation in quotations:
        total += float(quotation.total)


    form = QuotationForm.objects.all().first()
    # Create a PDF template using Django template
    template_path = 'pdf_invoice.html'  # Create a template for your PDF
    template = get_template(template_path)

    sp=quotations[0].quotation_sp
    # Retrieve the Service instance
    service_instance = inquiry.services
    # Convert the comma-separated string back to a list
    columns_list = service_instance.columns.split(',')
    columns_list.append('Total')

    data = []
    for quotation in quotations:
        datas = quotation.data.split(',*,')
        datas.append(quotation.total)
        data.append(datas)
    


    booking = Booking.objects.get(inquiry=inquiry)
    date=booking.booking_date
    service=booking.booking_service

    context = {'inquiry': inquiry,
                'quotations': quotations,
                'date':date,
                'service':sp,
                'phone':phone,
                'address':address,
                'email':email,
                'total':total,
                'form':form,
                'columns_list':columns_list,
                'data':data,
                'booking':booking,
                'sp_email':sp.email,
                'sp_phone':sp.phone
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


