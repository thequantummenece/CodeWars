import random

from django.shortcuts import get_object_or_404

from judge.types import TestCase

from .models import Problems, TestCases


def fetch_problem(question_id):
    return get_object_or_404(Problems, q_no=question_id)


def fetch_all_problems():
    return Problems.objects.all().order_by("q_no")


def fetch_random_problem(difficulty):
    q_no = list(
        Problems.objects.filter(q_difficulty=difficulty).values_list("q_no", flat=True)
    )
    if not q_no:
        raise Problems.DoesNotExist(f"No problems with difficulty {difficulty!r}")

    random_q_no = random.choice(q_no)
    return get_object_or_404(Problems, q_no=random_q_no)


def fetch_judge_cases(problem):
    return _to_judge_cases(TestCases.objects.filter(problem=problem))


def fetch_public_judge_cases(problem):
    return _to_judge_cases(
        TestCases.objects.filter(problem=problem, visibility="PUBLIC")
    )


def _to_judge_cases(rows):
    return [
        TestCase(row.test_case_no, row.test_case, row.expected_output)
        for row in rows.order_by("test_case_no")
    ]
