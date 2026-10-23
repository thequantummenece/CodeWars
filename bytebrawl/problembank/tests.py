from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import Http404
from django.test import TestCase

from judge.types import TestCase as JudgeCase
from .models import Problems, Submission, TestCases
from .selectors import (
    fetch_judge_cases,
    fetch_problem,
    fetch_public_judge_cases,
    fetch_random_problem,
)


def make_problem(q_no, difficulty="Easy"):
    return Problems.objects.create(
        q_no=q_no, q_title=f"P{q_no}", q_description="d", q_input_format="i",
        q_output_format="o", q_sample_io="s", q_tag="t", q_difficulty=difficulty,
    )


class SelectorTests(TestCase):
    def setUp(self):
        self.problem = make_problem(1)
        # Inserted out of order, so ordering has to come from test_case_no.
        for no, visibility in [(3, "PRIVATE"), (1, "PUBLIC"), (2, "PUBLIC")]:
            TestCases.objects.create(
                problem=self.problem, test_case_no=no, visibility=visibility,
                test_case=f"in{no}", expected_output=f"out{no}",
            )

    def test_fetch_problem_unknown_raises_404(self):
        with self.assertRaises(Http404):
            fetch_problem(999)

    def test_fetch_random_problem_returns_matching_difficulty(self):
        self.assertEqual(fetch_random_problem("Easy"), self.problem)

    def test_fetch_random_problem_empty_difficulty_raises_does_not_exist(self):
        with self.assertRaises(Problems.DoesNotExist):
            fetch_random_problem("Hard")

    def test_fetch_judge_cases_ordered_by_test_case_no(self):
        cases = fetch_judge_cases(self.problem)
        self.assertEqual([c.number for c in cases], [1, 2, 3])
        self.assertEqual(cases[0], JudgeCase(1, "in1", "out1"))

    def test_fetch_public_judge_cases_only_public(self):
        self.assertEqual([c.number for c in fetch_public_judge_cases(self.problem)], [1, 2])


class SubmissionTests(TestCase):
    def test_missing_verdict_is_rejected(self):
        user = User.objects.create_user("u", password="x")
        with self.assertRaises(IntegrityError):
            Submission.objects.create(user=user, problem=make_problem(1), code="", lang="python")
