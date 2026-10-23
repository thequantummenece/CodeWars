from django.shortcuts import render
from problembank.selectors import fetch_all_problems , fetch_problem

def questions(request):
    questions = fetch_all_problems()
    return render(request, 'learning/questions.html', {'questions': questions})

# Non-numeric ids never reach here (<int:> route); unknown ones 404 in fetch_problem.
def question_description(request ,question_id):
    question = fetch_problem(question_id=question_id)
    return render(request, 'learning/question_description.html', {'question': question})
