from django.shortcuts import render
from django.http import HttpResponse 
from problembank.selectors import fetch_all_problems , fetch_problem

def questions(request):
    questions = fetch_all_problems()
    return render(request, 'learning/questions.html', {'questions': questions})

def question_description(request ,question_id):
    if(not question_id.isdigit()):
        return HttpResponse("No Such Question Exist")
    question = fetch_problem(question_id=question_id)
    return render(request, 'learning/question_description.html', {'question': question})
