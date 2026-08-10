from django.shortcuts import render
from django.http import HttpResponse

def compete(request):
    return HttpResponse("This is Compete Page")