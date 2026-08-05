from django.contrib import admin
from .models import Problems, TestCases, Submission

# Register your models here.
admin.site.register(Problems)
admin.site.register(TestCases)
admin.site.register(Submission)