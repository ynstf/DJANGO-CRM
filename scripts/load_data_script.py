# load_data_script.py
from faker import Faker
from random import choice
from apps.dashboard.models import Language, Source, Nationality, Emirate, Service, Customer, Address, Inquiry
from apps.dashboard.models import Status,InquiryStatus
from apps.authentication.models import Employee
from django.db import transaction

fake = Faker()


@transaction.atomic
def run():

    status = ["new","connecting","pending","cancel","underproccess","send Q or B"]
    status_objs = [Status.objects.get_or_create(name=state)[0] for state in status]

    # Create Languages
    languages = ["Arabic", "French", "English", "Spanish"]
    language_objs = [Language.objects.get_or_create(name=lang)[0] for lang in languages]

    # Create Nationalities
    nationalities = ["Unknown", "arabic expat male", "arabic expat female", "company", "UAE male", "UAE female",
                    "Euroupe&american&Australia&Russia male", "Euroupe&american&Australia&Russia female",
                    "asia&africa male", "asia&africa Female"]
    nationality_objs = [Nationality.objects.get_or_create(name=nat)[0] for nat in nationalities]

    # Create Sources
    sources = ["from service provider", "website", "Direct booking", "from points", "affiliate marketing",
            "inbound calls", "outbound calls", "Instagram", "facebook", "linkedin", "tiktok", "snapchat",
            "telegram", "recommended customer", "whats up broadcast", "whats up marketing", "sms campaign",
            "email marketing"]
    source_objs = [Source.objects.get_or_create(name=src)[0] for src in sources]

    # Create Emirates
    emirates = ["Emara 1", "Emara 2", "Emara 3"]
    emirate_objs = [Emirate.objects.get_or_create(name=emirate)[0] for emirate in emirates]

    # Create Services
    services = ["electric", "climatisation", "plumber"]
    service_objs = [Service.objects.get_or_create(name=service)[0] for service in services]

    # Create Employees
    employees = Employee.objects.values_list('id', flat=True)
    if not employees:
        print("No employees found. Create employees before running this script.")
        return

    # Create Customers with Addresses and Inquiries
    for _ in range(100):
        employee_id = choice(employees)

        # Choose valid foreign key values for nationality and language
        nationality_id = choice(Nationality.objects.all()).id
        language_id = choice(Language.objects.all()).id

        customer = Customer.objects.create(
            employee_id=employee_id,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            gender=choice(['male', 'female']),
            nationality_id=nationality_id,
            language_id=language_id,
            trn=fake.uuid4(),
        )
        
        # Choose valid foreign key values for emirate
        emirate_id = choice(Emirate.objects.all()).id

        address = Address.objects.create(
            customer=customer,
            address_name=fake.street_name(),
            type=choice(['house', 'company']),
            emirate_id=emirate_id,
            description_location=fake.text(),
            location=fake.address(),
        )

        service_id = choice(Service.objects.all()).id  # Choose a valid service ID
        source_id = choice(Source.objects.all()).id  # Choose a valid source ID

        inquiry = Inquiry.objects.create(
            customer=customer,
            address=address,
            date_inq=fake.date_this_year(),
            services_id=service_id,
            source_id=source_id,
            description=fake.text(),
        )


        state_name = choice(status)

        state = Status.objects.get(name= state_name)
        inquiry_state = InquiryStatus.objects.create(
            inquiry=inquiry,
            status = state
        )
