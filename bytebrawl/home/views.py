from django.contrib import messages
from django.shortcuts import render

from .models import Contact


def home(request):
    return render(request, 'home/home.html')


def about(request):
    return render(request, 'home/about.html')


def contact(request):
    context = {}
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        if name and email and message:
            # The model has no subject column, so it leads the stored message.
            content = f'{subject}\n\n{message}' if subject else message
            Contact.objects.create(name=name, email=email, content=content)
            context['sent'] = True
            context['name'] = name
        else:
            messages.error(request, 'Name, email and message are required')
    return render(request, 'home/contact.html', context)
