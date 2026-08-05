from django.shortcuts import render


def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


def contact(request):
    context = {}
    if request.method == 'POST':
        context['sent'] = True
        context['name'] = request.POST.get('name', '')
    return render(request, 'contact.html', context)
