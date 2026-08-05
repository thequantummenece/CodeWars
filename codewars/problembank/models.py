from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

class Problems(models.Model):
    q_id = models.AutoField(primary_key=True)
    q_no = models.IntegerField(unique=True)
    q_title = models.CharField(max_length=100)
    q_description = models.TextField()
    q_input_format = models.TextField() # This will inclued Constrainsts 
    q_output_format = models.TextField() # This will inclued Constrainsts 
    q_sample_io = models.TextField() 
    q_tag = models.CharField(max_length=30)
    q_difficulty = models.CharField(
        max_length=10,
        choices=[("Easy","Easy"),("Medium","Medium"),("Hard","Hard")],
        default="Medium",
    )
    date_published = models.DateField(default=datetime.now)

class TestCases(models.Model):
    q_id = models.ForeignKey(Problems, on_delete=models.CASCADE)
    test_case_no = models.IntegerField(unique=False,default=1)
    visiblity = models.CharField(
        max_length=20,
        choices=[
            ("PUBLIC", "PUBLIC"),
            ("PRIVATE", "PRIVATE"),
        ],
        default="PRIVATE",
    )
    test_case = models.TextField()
    expected_output = models.TextField()

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
        default="WA",
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

