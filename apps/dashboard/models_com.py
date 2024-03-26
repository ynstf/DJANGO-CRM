from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=50)
    columns = models.TextField(blank=True, null=True)
    reminder_time =  models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

class SuperProvider(models.Model):
    name = models.CharField(max_length=50)
    #service = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True)
    service = models.ManyToManyField(Service, blank=True, null=True)
    trn = models.CharField(max_length=50, blank=True, null=True)
    search_number = models.IntegerField(blank=True, null=True)
    phone_Number = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name
