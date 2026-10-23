from django.db import models
from datetime import date
from django.contrib.auth.models import User

class Problems(models.Model):
    q_id = models.AutoField(primary_key=True)
    q_no = models.IntegerField(unique=True)
    q_title = models.CharField(max_length=100)
    q_description = models.TextField()
    q_input_format = models.TextField()  # Constraints are inlined here.
    q_output_format = models.TextField()
    q_sample_io = models.TextField() 
    q_tag = models.CharField(max_length=30)
    q_difficulty = models.CharField(
        max_length=10,
        choices=[("Easy","Easy"),("Medium","Medium"),("Hard","Hard")],
        default="Medium",
    )
    date_published = models.DateField(default=date.today)

    def __str__(self):
        return f"{self.q_no}. {self.q_title}"

class TestCases(models.Model):
    problem = models.ForeignKey(Problems, on_delete=models.CASCADE)
    test_case_no = models.IntegerField(unique=False,default=1)
    visibility = models.CharField(
        max_length=20,
        choices=[
            ("PUBLIC", "PUBLIC"),
            ("PRIVATE", "PRIVATE"),
        ],
        default="PRIVATE",
    )
    test_case = models.TextField()
    expected_output = models.TextField()

    class Meta:
        ordering = ["test_case_no"]

    def __str__(self):
        return f"{self.problem} - case {self.test_case_no}"

class Submission(models.Model):
    VERDICT_CHOICES = [
            ("AC", "Accepted"),
            ("WA", "Wrong Answer"),
            ("TLE", "Time Limit Exceeded"),
            ("RE", "Runtime Error"),
            ("MLE", "Memory Limit Exceeded"),
        ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problems,on_delete=models.CASCADE)
    code = models.TextField()
    lang = models.CharField(max_length=20)
    verdict = models.CharField(
        max_length=3,
        choices=VERDICT_CHOICES,
    )
    runtime_ms = models.PositiveIntegerField(null=True, blank=True)
    memory_kb = models.PositiveIntegerField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Without this a forgotten verdict saves as "" (CharField's implicit default).
        # Meta can't see VERDICT_CHOICES, so keep this list in step with it.
        constraints = [
            models.CheckConstraint(
                condition=models.Q(verdict__in=["AC", "WA", "TLE", "RE", "MLE"]),
                name="submission_verdict_valid",
            ),
        ]

    def __str__(self):
        return f"{self.user} - {self.problem} - {self.verdict}"

