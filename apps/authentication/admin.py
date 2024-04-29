from django.contrib import admin
from .models import Employee, Position,Permission

# Register your models here.
admin.site.register(Position)
admin.site.register(Permission)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name','last_name','sp')