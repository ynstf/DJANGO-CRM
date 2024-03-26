from django.http import JsonResponse
from ..models import Language, Nationality, Source, Service, Status, SuperProvider

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
                service_names = [service.name for service in services]
                return JsonResponse({'services': service_names})
            except SuperProvider.DoesNotExist:
                return JsonResponse({'error': 'Super provider not found.'}, status=404)
        else:
            return JsonResponse({'error': 'Super provider ID is required.'}, status=400)
    else:
        # Handle non-AJAX requests
        return JsonResponse({'error': 'This endpoint is only accessible via AJAX.'}, status=400)
