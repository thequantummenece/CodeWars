from django.urls import path
from . import views

urlpatterns = [
    path('',views.questions, name='questions'),
    path('<str:question_id>/',views.question_description, name='question_description')
]