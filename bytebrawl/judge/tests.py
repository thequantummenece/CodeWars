"""Pure tests: no database, no Django."""

import unittest

from judge import reference
from judge.core import grade
from judge.types import CaseResult, TestCase, Verdict


class TypesTests(unittest.TestCase):
    def test_first_failure_is_first_failing_case(self):
        verdict = Verdict(
            "WA", [CaseResult(1, True), CaseResult(2, False), CaseResult(3, False)]
        )
        self.assertEqual(verdict.first_failure.number, 2)

    def test_first_failure_is_none_when_all_pass(self):
        self.assertIsNone(Verdict("AC", [CaseResult(1, True)]).first_failure)


class GradeStubTests(unittest.TestCase):
    def test_stub_never_accepts(self):
        cases = [TestCase(1, "1", "1"), TestCase(2, "2", "2")]
        verdict = grade("print(input())", "python", cases)
        self.assertEqual(verdict.code, "WA")
        self.assertEqual([r.number for r in verdict.results], [1, 2])
        self.assertEqual(verdict.first_failure.number, 1)


class ReferenceTests(unittest.TestCase):
    def test_two_sum(self):
        self.assertEqual(reference.solve_two_sum("4 9\n2 7 11 15"), "0 1")

    def test_valid_parentheses(self):
        self.assertEqual(reference.solve_valid_parentheses("([]{})"), "YES")
        self.assertEqual(reference.solve_valid_parentheses("(]"), "NO")

    def test_edit_distance(self):
        self.assertEqual(reference.solve_edit_distance("horse\nros"), "3")

    def test_trapping_rain(self):
        self.assertEqual(
            reference.solve_trapping_rain("12\n0 1 0 2 1 0 1 3 2 1 2 1"), "6"
        )
