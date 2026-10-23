"""What the judge takes in and hands back. Plain data, no Django."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TestCase:
    number: int
    input: str
    expected_output: str


@dataclass(frozen=True)
class CaseResult:
    number: int
    passed: bool
    runtime_ms: int | None = None
    memory_kb: int | None = None


@dataclass(frozen=True)
class Verdict:
    code: str  # one of Submission.VERDICT_CHOICES: AC, WA, TLE, RE, MLE
    results: list[CaseResult] = field(default_factory=list)
    runtime_ms: int | None = None
    memory_kb: int | None = None

    @property
    def first_failure(self):
        return next((r for r in self.results if not r.passed), None)
