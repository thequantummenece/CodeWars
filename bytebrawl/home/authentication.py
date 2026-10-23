from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import HttpResponse, redirect


def blogin(request):
    if request.method =="POST":
        #parameters for post
        loginusername = request.POST.get("lusername", "")
        loginpassword = request.POST.get("Password", "")
        if not loginusername or not loginpassword:
            messages.error(request,"Username and password are required")
            return redirect('home')

        user = authenticate(username = loginusername,password = loginpassword)
        if user is None:
            messages.error(request,"Invalid Credentials")
            return redirect('home')
        else:
            login(request, user)
            messages.success(request,"Successfully logged in ")
            return redirect('home')
    else:
        return HttpResponse("Not a Valid Login")

def blogout(request):
    if request.method == "GET":
        logout(request)
        messages.warning(request, "You have been logged out")
        return redirect('home')
    return redirect('home')

def signin(request):
    if request.method == "POST":
        # parameters
        fname = request.POST.get('inputfname', '')
        lname = request.POST.get('inputlname', '')
        username = request.POST.get('username', '')
        password = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        email = request.POST.get('inputemail', '')

        if not all([fname, lname, username, password, password2, email]):
            messages.add_message(request, messages.ERROR, 'All fields are required')
            return redirect('home')

        if User.objects.filter(username=username).exists():
            messages.add_message(request, messages.ERROR, 'User Name already Exist')
            return redirect('home')
        
        if(password2 == password):
            try:
                candidate = User(username=username, email=email, first_name=fname, last_name=lname)
                validate_password(password, candidate)
            except ValidationError as e:
                messages.add_message(request, messages.ERROR, ' '.join(e.messages))
                return redirect('home')

            #creating user
            myuser = User.objects.create_user(username,email,password)
            myuser.first_name = fname
            myuser.last_name = lname
            myuser.save()
            messages.add_message(request, messages.SUCCESS, 'your account has been created')
            return redirect('home')

        else:
            messages.add_message(request, messages.ERROR, 'Error Signing in Passwords Dont Match')
            return redirect('home')

    return redirect('home')