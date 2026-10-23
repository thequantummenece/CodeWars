import random

from .models import Problems,TestCases,Submission
from django.shortcuts import get_object_or_404

def fetch_problem(question_id):
    try:
        return get_object_or_404(Problems, q_no = question_id)
    except Exception as e:
        raise e

def fetch_all_problems():
    try:
        return Problems.objects.all().order_by("q_no")
    except Exception as e:
        raise e

def fetch_random_problem(difficulty):
    try:
        q_no =list(
            Problems.objects.filter(
                q_difficulty=difficulty
                ).values_list(
                    'q_no',
                    flat=True
                )
            )
        if not q_no:
            raise Problems.DoesNotExist(f"No problems with difficulty {difficulty!r}")

        random_q_no = random.choice(q_no)
        return get_object_or_404(Problems, q_no = random_q_no)

    except Exception as e:
        raise e


    
