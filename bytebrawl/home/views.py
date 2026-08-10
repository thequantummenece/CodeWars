from django.shortcuts import render


def home(request):
    return render(request, 'home/home.html')


def about(request):
    return render(request, 'home/about.html')


def contact(request):
    context = {}
    if request.method == 'POST':
        context['sent'] = True
        context['name'] = request.POST.get('name', '')
    return render(request, 'home/contact.html', context)
