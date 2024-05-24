
import django.contrib.auth
from django.http import JsonResponse
from ..models import Language, Nationality, Source, Service, Status, SuperProvider, PhoneNumber
from apps.authentication.models import Employee

def get_languages_view(request):
    languages = [l.name for l in Language.objects.all()]
    return JsonResponse({'data': languages})

def get_nationalities_view(request):
    nationalities = [n.name for n in Nationality.objects.all()]
    return JsonResponse({'data': nationalities})

def get_sources_view(request):
    sources = [s.name for s in Source.objects.all()]
    return JsonResponse({'data': sources})

def get_services_view(request):
    services = [srv.name for srv in Service.objects.all()]
    return JsonResponse({'data': services})

def get_status_view(request):
    states = [stt.name for stt in Status.objects.all()]
    return JsonResponse({'data': states})


def get_services_by_sp_view(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Retrieve the super provider ID from the request parameters
        super_provider_id = request.GET.get('super_provider_id')

        # Retrieve services based on the super provider ID
        if super_provider_id:
            try:
                super_provider = SuperProvider.objects.get(id=super_provider_id)
                services = super_provider.service.all()
                service_names = [ {"name":service.name,"id":service.number} for service in services]
        
                return JsonResponse({'services': service_names})
            #{"name":service_names,'id':}
            except SuperProvider.DoesNotExist:
                return JsonResponse({'error': 'Super provider not found.'}, status=404)
        else:
            return JsonResponse({'error': 'Super provider ID is required.'}, status=400)
    else:
        # Handle non-AJAX requests
        return JsonResponse({'error': 'This endpoint is only accessible via AJAX.'}, status=400)


def get_employees_by_sp_view(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Retrieve the super provider ID from the request parameters
        super_provider_id = request.GET.get('super_provider_id')

        # Retrieve services based on the super provider ID
        if super_provider_id:
            try:
                super_provider = SuperProvider.objects.get(id=super_provider_id)
                # Get all employees with the specific SuperProvider
                employees_with_sp = Employee.objects.filter(sp=super_provider)
                employees = [ {"name":f'{employee.first_name} {employee.last_name}',"id":employee.id} for employee in employees_with_sp]
        
                return JsonResponse({'employees': employees})
            #{"name":service_names,'id':}
            except SuperProvider.DoesNotExist:
                return JsonResponse({'error': 'Super provider not found.'}, status=404)
        else:
            return JsonResponse({'error': 'Super provider ID is required.'}, status=400)
    else:
        # Handle non-AJAX requests
        return JsonResponse({'error': 'This endpoint is only accessible via AJAX.'}, status=400)


"""
def check_phone_number(request):
    phone_number = request.GET.get('phone_number', None)
    if phone_number:
        try:
            phone_record = PhoneNumber.objects.get(number=phone_number)
            customer = phone_record.customer
            customer_data = {
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'id': customer.id
            }
            return JsonResponse({'exists': True, 'customer': customer_data})
        except PhoneNumber.DoesNotExist:
            return JsonResponse({'exists': False})
    return JsonResponse({'exists': False})

"""
def check_phone_number(request):
    phone_number = request.GET.get('phone_number', None)
    if phone_number:
        try:
            phone_record = PhoneNumber.objects.get(number=phone_number)
            customer = phone_record.customer
            customer_data = {
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'gender': customer.gender,
                'nationality': customer.nationality.id if customer.nationality else None,
                'language': customer.language.id if customer.language else None,
                'trn': customer.trn,
                'id': customer.id
            }
            return JsonResponse({'exists': True, 'customer': customer_data})
        except PhoneNumber.DoesNotExist:
            return JsonResponse({'exists': False})
    return JsonResponse({'exists': False})
