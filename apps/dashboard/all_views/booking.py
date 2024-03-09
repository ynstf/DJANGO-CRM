from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.loader import get_template
from web_project.template_helpers.theme import TemplateHelper
from web_project import TemplateLayout

from ..models import Inquiry, Quotation, QuotationForm, Customer, PhoneNumber, Email, Service, Booking
from apps.authentication.models import Employee,Permission
from apps.dashboard.models import (Inquiry, InquiryStatus, Language, Nationality, InquiryNotify,
    Source, Status)
from django.http import JsonResponse


def make_inq_underproccess(request,inq_id):
    underproccess = Status.objects.get(name = "underproccess")
    inquiry = Inquiry.objects.get(id = inq_id)
    inq_state = InquiryStatus.objects.get(inquiry = inquiry)
    inq_state.status = underproccess
    inq_state.save()
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

        print('quotation-detail',request.POST.getlist('quotation-detail'))
        print('quotation-a ',request.POST.getlist('quotation-a'))
        print('quotation-b',request.POST.getlist('quotation-b'))
        print('quotation-price',request.POST.getlist('quotation-price'))
        print('quotation-quantity',request.POST.getlist('quotation-quantity'))

        inquiry = Inquiry.objects.get(id=id)
        customer_id = inquiry.customer.id
        customer = Customer.objects.get(id=customer_id)
        employee_id = request.user.employee.id
        employee = Employee.objects.get(id=employee_id)

        # Retrieve the Service instance
        service_instance = inquiry.services
        # Convert the comma-separated string back to a list
        columns_list = service_instance.columns.split(',')
        print('columns : ',columns_list)

        srv_id = quotation_service
        quotation_service = Service.objects.get(id=srv_id)

        lent = request.POST.getlist('quotation-price')
        print("lent : ",lent)
        for i in range(len(lent)):
            data = []
            for field in columns_list:
                print(f'quotation-{field}')
                details = request.POST.getlist(f'quotation-{field}')[i]
                data.append(details)
            total = float(data[-1])*float(data[-2])
            columns_str = ",*,".join(data)
            print(columns_str)
            
            booking = Booking(
                employee=employee,
                customer=customer,
                inquiry=inquiry,
                booking_service=quotation_service,
                booking_date=quotation_date,
                data = columns_str,
                total=total
            )
            booking.save()

            print()
        
        return redirect('make_inq_underproccess', inq_id=id)



    
    date=quotations[0].quotation_date
    service=quotations[0].quotation_service

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
                }
    
    context = TemplateLayout.init(request, context)
    return render(request, 'booking/make_booking.html',context)
