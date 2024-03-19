from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=50)
    columns = models.TextField(blank=True, null=True)
    reminder_time =  models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name
