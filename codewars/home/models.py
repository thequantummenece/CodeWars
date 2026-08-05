from django.db import models

# Create your models here.
class Contact(models.Model):
    Sno = models.AutoField(primary_key=True)
    name = models.CharField(max_length= 100)
    email = models.CharField(max_length= 250)
    phone = models.CharField(max_length = 14)
    content = models.TextField()

    def __str__(self):
        return "This is from " + self.name + '_' + self.email