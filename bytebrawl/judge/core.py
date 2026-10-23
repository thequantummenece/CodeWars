"""Grading entry point."""

from judge.types import CaseResult, Verdict


def grade(code, language, cases):
    """Grade `code` against `cases` and return a Verdict.

    STUB: user code is never executed. Every case is reported as failed, so the
    stub can't mark a problem solved once it is wired to a request.
    shortcut: hardcoded WA, replace with sandboxed execution (TODO §1 Sandbox).
    """
    return Verdict(
        code="WA",
        results=[CaseResult(number=case.number, passed=False) for case in cases],
    )
