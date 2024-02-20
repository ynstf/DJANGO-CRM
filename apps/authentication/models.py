from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create groups for different roles
agent_group, created = Group.objects.get_or_create(name='agent')
supervisor_group, created = Group.objects.get_or_create(name='supervisor')
admin_group, created = Group.objects.get_or_create(name='admin')

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    position = models.CharField(max_length=16, choices=[('admin', 'admin'), ('agent', 'agent'), ('supervisor', 'supervisor')], blank=True, null=True)
    # Add more fields as needed


    def __str__(self):
        return f"{self.first_name} {self.last_name}"



@receiver(post_save, sender=Employee)
def assign_group(sender, instance, created, **kwargs):
    # Assign user to group based on position
    if created:
        if instance.position == 'agent':
            instance.user.groups.add(agent_group)
        elif instance.position == 'supervisor':
            instance.user.groups.add(supervisor_group)
        elif instance.position == 'admin':
            instance.user.groups.add(admin_group)
