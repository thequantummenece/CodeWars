from django.urls import path
from . import views
from . import authentication

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('login/', authentication.blogin, name='login'),
    path('logout/', authentication.blogout, name='logout'),
    path('signup/', authentication.signin, name='signup'),
]
