from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from apps.authentication.models import Employee
from apps.authentication.models import Position, Permission, Service
from django.contrib.auth.models import Group
from apps.dashboard.models_com import SuperProvider

"""
dashboard test
inquiries list test
add customers test
customer list test
add service test
services list test
add employee test
employee list test
"""

Services = [
    {'name':"electric",'column':'details,price,quantity'},
    {'name':"climatisation",'column':'details,price,quantity'},
    {'name':"plumber",'column':'details,price,quantity'},
]

Positions = [
    'admin',
    'call center',
    'super provider',
    'team leader'
]
sps = [
    'sp1',
    'sp2',
    'sp3',
    'sp4'
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

class BaseTest(TestCase):
    def setUp(self):
        # Create Services
        for service in Services:
            srv, created = Service.objects.get_or_create(name=service['name'], columns=service['column'])
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


        # Create sps
        for sp in sps:
            spr, created = SuperProvider.objects.get_or_create(name=sp)
            if created:
                spr.save()

        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        superp = Position.objects.get(name="super provider")
        service = Service.objects.get(name="electric")
        sp = SuperProvider.objects.get(name="sp1")

        self.employee = Employee.objects.create(
            user=self.user,
            first_name="test",
            last_name='test',
            email='test@test.com',
            phone_number='0648474648',
            position=superp,
            sp=sp
        )

        # Create groups for different roles
        call_center_group, created = Group.objects.get_or_create(name='call_center')
        provider_group, created = Group.objects.get_or_create(name='provider')
        admin_group, created = Group.objects.get_or_create(name='admin')
        team_leader_group, created = Group.objects.get_or_create(name='team_leader')

        self.employee.permissions.set([Permission.objects.get(name="inquiry list")])
        self.employee.user.groups.add(provider_group)


class DashboardTest(BaseTest):
    # Add similar test methods for your other routes
    def test_dashboard_route_authenticated(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')

        # Use the reverse function to get the URL for the route
        url = reverse('dashboard')

        # Make a GET request to the URL
        response = self.client.get(url)

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)


class InquiriesListTest(BaseTest):
    def test_inquiries_list_route_authenticated(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')

        # Use the reverse function to get the URL for the 'inquiries_list' route
        url = reverse('inquiries_list')

        # Make a GET request to the URL
        response = self.client.get(url)

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)


class AddCustomersTest(BaseTest):
    def setUp(self):
        # Create Services
        for service in Services:
            srv, created = Service.objects.get_or_create(name=service['name'], columns=service['column'])
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

        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        sp = Position.objects.get(name="call center")

        self.employee = Employee.objects.create(
            user=self.user,
            first_name="test",
            last_name='test',
            email='test@test.com',
            phone_number='0648474648',
            position=sp,
        )

        # Create groups for different roles
        call_center_group, created = Group.objects.get_or_create(name='call_center')
        provider_group, created = Group.objects.get_or_create(name='provider')
        admin_group, created = Group.objects.get_or_create(name='admin')
        team_leader_group, created = Group.objects.get_or_create(name='team_leader')

        self.employee.permissions.set([Permission.objects.get(name="add customer")])
        self.employee.user.groups.add(call_center_group)

    # Add similar test methods for your other routes
    def test_add_customers_route_authenticated(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')

        # Use the reverse function to get the URL for the route
        url = reverse('add_customer')

        # Make a GET request to the URL
        response = self.client.get(url)

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)


class CustomerListTest(BaseTest):
    def setUp(self):
        # Create Services
        for service in Services:
            srv, created = Service.objects.get_or_create(name=service['name'], columns=service['column'])
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

        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        sp = Position.objects.get(name="call center")

        self.employee = Employee.objects.create(
            user=self.user,
            first_name="test",
            last_name='test',
            email='test@test.com',
            phone_number='0648474648',
            position=sp,
        )

        # Create groups for different roles
        call_center_group, created = Group.objects.get_or_create(name='call_center')
        provider_group, created = Group.objects.get_or_create(name='provider')
        admin_group, created = Group.objects.get_or_create(name='admin')
        team_leader_group, created = Group.objects.get_or_create(name='team_leader')

        self.employee.permissions.set([Permission.objects.get(name="customer list")])
        self.employee.user.groups.add(call_center_group)

    # Add similar test methods for your other routes
    def test_customer_list_route_authenticated(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')

        # Use the reverse function to get the URL for the route
        url = reverse('customer_list')

        # Make a GET request to the URL
        response = self.client.get(url)

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)


class AddServiceTest(BaseTest):
    def setUp(self):
        # Create Services
        for service in Services:
            srv, created = Service.objects.get_or_create(name=service['name'], columns=service['column'])
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

        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        sp = Position.objects.get(name="admin")

        self.employee = Employee.objects.create(
            user=self.user,
            first_name="test",
            last_name='test',
            email='test@test.com',
            phone_number='0648474648',
            position=sp,
        )

        # Create groups for different roles
        call_center_group, created = Group.objects.get_or_create(name='call_center')
        provider_group, created = Group.objects.get_or_create(name='provider')
        admin_group, created = Group.objects.get_or_create(name='admin')
        team_leader_group, created = Group.objects.get_or_create(name='team_leader')

        self.employee.user.groups.add(admin_group)

    # Add similar test methods for your other routes
    def test_add_service_route_authenticated(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')

        # Use the reverse function to get the URL for the route
        url = reverse('add_service')

        # Make a GET request to the URL
        response = self.client.get(url)

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)


class ServicesListTest(BaseTest):
    def setUp(self):
        # Create Services
        for service in Services:
            srv, created = Service.objects.get_or_create(name=service['name'], columns=service['column'])
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

        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        sp = Position.objects.get(name="admin")

        self.employee = Employee.objects.create(
            user=self.user,
            first_name="test",
            last_name='test',
            email='test@test.com',
            phone_number='0648474648',
            position=sp,
        )

        # Create groups for different roles
        call_center_group, created = Group.objects.get_or_create(name='call_center')
        provider_group, created = Group.objects.get_or_create(name='provider')
        admin_group, created = Group.objects.get_or_create(name='admin')
        team_leader_group, created = Group.objects.get_or_create(name='team_leader')

        self.employee.user.groups.add(admin_group)

    # Add similar test methods for your other routes
    def test_services_list_route_authenticated(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')

        # Use the reverse function to get the URL for the route
        url = reverse('services_list')

        # Make a GET request to the URL
        response = self.client.get(url)

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)


class AddEmployeeTest(BaseTest):
    def setUp(self):
        # Create Services
        for service in Services:
            srv, created = Service.objects.get_or_create(name=service['name'], columns=service['column'])
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

        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        sp = Position.objects.get(name="admin")

        self.employee = Employee.objects.create(
            user=self.user,
            first_name="test",
            last_name='test',
            email='test@test.com',
            phone_number='0648474648',
            position=sp,
        )

        # Create groups for different roles
        call_center_group, created = Group.objects.get_or_create(name='call_center')
        provider_group, created = Group.objects.get_or_create(name='provider')
        admin_group, created = Group.objects.get_or_create(name='admin')
        team_leader_group, created = Group.objects.get_or_create(name='team_leader')

        self.employee.user.groups.add(admin_group)

    # Add similar test methods for your other routes
    def test_add_employee_route_authenticated(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')

        # Use the reverse function to get the URL for the route
        url = reverse('add_employee')

        # Make a GET request to the URL
        response = self.client.get(url)

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)


class EmployeeListTest(BaseTest):
    def setUp(self):
        # Create Services
        for service in Services:
            srv, created = Service.objects.get_or_create(name=service['name'], columns=service['column'])
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

        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        sp = Position.objects.get(name="admin")

        self.employee = Employee.objects.create(
            user=self.user,
            first_name="test",
            last_name='test',
            email='test@test.com',
            phone_number='0648474648',
            position=sp,
        )

        # Create groups for different roles
        call_center_group, created = Group.objects.get_or_create(name='call_center')
        provider_group, created = Group.objects.get_or_create(name='provider')
        admin_group, created = Group.objects.get_or_create(name='admin')
        team_leader_group, created = Group.objects.get_or_create(name='team_leader')

        self.employee.user.groups.add(admin_group)

    # Add similar test methods for your other routes
    def test_employee_list_route_authenticated(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')

        # Use the reverse function to get the URL for the route
        url = reverse('employee_list')

        # Make a GET request to the URL
        response = self.client.get(url)

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)