from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, HttpResponse, redirect

def blogin(request):
    if request.method =="POST":
        #parameters for post
        loginusername = request.POST["lusername"]
        loginpassword = request.POST["Password"]

        user = authenticate(username = loginusername,password = loginpassword)
        if user is None:
            messages.error(request,"Invalid Credentials")
            return redirect('home')
        else:
            login(request, user)
            messages.success(request,"Successfully logged in ")
            return redirect('home')
    else:return HttpResponse("Not a Valid Login")

def blogout(request):
    if request.method == "GET":
        logout(request)
        messages.warning(request, "You have been logged out")
        return redirect('home')
    return redirect('home')

def signin(request):
    if request.method == "POST":
        # parameters
        fname = request.POST['inputfname']
        lname = request.POST['inputlname']
        username = request.POST['username']
        password = request.POST['password1']
        password2 = request.POST['password2']
        email = request.POST['inputemail']

        if User.objects.filter(username=username).exists():
            messages.add_message(request, messages.ERROR, 'User Name already Exist')
            return redirect('home')
        
        if(password2 == password):
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