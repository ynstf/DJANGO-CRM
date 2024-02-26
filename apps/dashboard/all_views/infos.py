from django.http import JsonResponse
from ..models import Language, Nationality, Source

def get_languages_view(request):
    languages = [l.name for l in Language.objects.all()]
    return JsonResponse({'data': languages})

def get_nationalities_view(request):
    nationalities = [n.name for n in Nationality.objects.all()]
    return JsonResponse({'data': nationalities})

def get_sources_view(request):
    sources = [s.name for s in Source.objects.all()]
    return JsonResponse({'data': sources})
