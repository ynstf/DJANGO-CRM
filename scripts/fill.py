# fill.py

from apps.dashboard.models import Language, Source, Nationality, Emirate, Service
from apps.authentication.models import Position, Permission

def run():
    Languages = [
        "Arabic",
        "French",
        "English",
        "Spanish",
    ]

    Nationalities = [
        "Unknown",
        "arabic expat male",
        "arabic expat female",
        "company",
        "UAE male",
        "UAE female",
        "Euroupe&american&Australia&Russia male",
        "Euroupe&american&Australia&Russia female",
        "asia&africa male",
        "asia&africa Female",
    ]

    Sources = [
        "from service provider",
        "website",
        "Direct booking",
        "from points",
        "affiliate marketing",
        "inbound calls",
        "out bound calls",
        "Instagram",
        "facebook",
        "linkedin",
        "tiktok",
        "snapchat",
        "telegram",
        "recommended customer",
        "whats up broadcast",
        "whats up marketing",
        "sms campaign",
        "email marketing",
    ]

    Emirates = [
        "Emara 1",
        "Emara 2",
        "Emara 3",
    ]

    Services = [
        "electric",
        "climatisation",
        "plumber",
    ]

    Positions = [
        'admin',
        'call center',
        'super provider',
        'team leader'
    ]

    Permissions = [
        "extract quotations",

        "customer list",
        "see customer info",
        "edit customer",
        "add customer",

        "inquiry list",
        "inquiry info",
        "make quotation",
        "edit quotation",

    ]

    # Create Languages
    for language in Languages:
        lang, created = Language.objects.get_or_create(name=language)
        if created:
            lang.save()

    # Create Nationalities
    for nationality in Nationalities:
        nat, created = Nationality.objects.get_or_create(name=nationality)
        if created:
            nat.save()

    # Create Sources
    for source in Sources:
        src, created = Source.objects.get_or_create(name=source)
        if created:
            src.save()

    # Create Emirates
    for emirate in Emirates:
        emr, created = Emirate.objects.get_or_create(name=emirate)
        if created:
            emr.save()

    # Create Services
    for service in Services:
        srv, created = Service.objects.get_or_create(name=service)
        if created:
            srv.save()

    # Create Position
    for position in Positions:
        ps, created = Position.objects.get_or_create(name=position)
        if created:
            ps.save()

    # Create Permission
    for permission in Permissions:
        prm, created = Permission.objects.get_or_create(name=permission)
        if created:
            prm.save()
