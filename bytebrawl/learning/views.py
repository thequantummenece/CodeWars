from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse ,JsonResponse
from problembank.models import Problems,TestCases,Submission

def questions(request):
    questions = Problems.objects.all()
    return render(request, 'questions.html', {'questions': questions})

def question_description(request ,question_id):
    if( not question_id.isdigit()):
        return HttpResponse("No Such Question Exist")
    question = get_object_or_404(Problems, q_no=question_id)
    return render(request, 'question_description.html', {'question': question})
