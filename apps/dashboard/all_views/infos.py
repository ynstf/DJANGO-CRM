from django.http import JsonResponse
from ..models import Language, Nationality, Source, Service, Status

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
