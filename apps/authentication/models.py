from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.dashboard.models_com import Service, SuperProvider


class Position(models.Model):
    name = models.CharField(max_length=36, unique=True)
    def __str__(self):
        return self.name

class Permission(models.Model):
    name = models.CharField(max_length=36, unique=True)
    def __str__(self):
        return self.name

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True)
    sp = models.ForeignKey(SuperProvider, on_delete=models.SET_NULL, blank=True, null=True)
    permissions = models.ManyToManyField(Permission, blank=True, null=True)
    is_online = models.BooleanField(default=False)

    search_number = models.IntegerField(blank=True, null=True)
    columns = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# Create groups for different roles
call_center_group, created = Group.objects.get_or_create(name='call_center')
provider_group, created = Group.objects.get_or_create(name='provider')
admin_group, created = Group.objects.get_or_create(name='admin')
team_leader_group, created = Group.objects.get_or_create(name='team_leader')

accountant_group, created = Group.objects.get_or_create(name='accountant')
financial_group, created = Group.objects.get_or_create(name='financial')

@receiver(post_save, sender=Employee)
def assign_group(sender, instance, created, **kwargs):
    # Assign user to group based on position
    if created:
        if instance.position.name == 'call center':
            instance.user.groups.add(call_center_group)
        elif instance.position.name == 'super provider':
            instance.user.groups.add(provider_group)
        elif instance.position.name == 'admin':
            instance.user.groups.add(admin_group)
        elif instance.position.name == 'team leader':
            instance.user.groups.add(team_leader_group)

        elif instance.position.name == 'accountant':
            instance.user.groups.add(accountant_group)
        elif instance.position.name == 'financial':
            instance.user.groups.add(financial_group)

