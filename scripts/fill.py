# fill.py

from apps.dashboard.models import Language, Source, Nationality, Emirate, Service, Status
from apps.authentication.models import Position, Permission

def run():
    Languages = ["Arabic", "French", "English", "Spanish"]

    Nationalities = ["Unknown", "arabic expat male", "arabic expat female", "company", "UAE male", "UAE female", "Euroupe&american&Australia&Russia male", "Euroupe&american&Australia&Russia female", "asia&africa male", "asia&africa Female"]

    Sources = ["from service provider", "website", "Direct booking", "from points", "affiliate marketing", "inbound calls", "out bound calls", "Instagram", "facebook", "linkedin", "tiktok", "snapchat", "telegram", "recommended customer", "whats up broadcast", "whats up marketing", "sms campaign", "email marketing"]

    Emirates = ["Emara 1", "Emara 2", "Emara 3"]

    Services = [{'name':"electric",'column':'details,price,quantity'}, {'name':"climatisation",'column':'details,price,quantity'}, {'name':"plumber",'column':'details,price,quantity'}]

    Positions = ['admin', 'call center', 'super provider', 'team leader','accountant','financial']

    Permissions = ["extract quotations", "customer list", "see customer info", "edit customer", "add customer", "inquiry list", "inquiry info", "make quotation", "edit quotation"]

    status = ["new", "connecting", "pending", "cancel", "done", "underproccess", "send Q", "send B", "complain", 'reminder']

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
        srv, created = Service.objects.get_or_create(name=service['name'], columns=service['column'])
        if created:
            srv.save()

    # Create Positions
    for position in Positions:
        ps, created = Position.objects.get_or_create(name=position)
        if created:
            ps.save()

    # Create Permissions
    for permission in Permissions:
        prm, created = Permission.objects.get_or_create(name=permission)
        if created:
            prm.save()

    # Create status
    for state in status:
        sts, created = Status.objects.get_or_create(name=state)
        if created:
            sts.save()
