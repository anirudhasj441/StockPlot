import json
from urllib import response
from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User

# Create your views here.

def index(request):

    return render(request, 'home/index.html')

# APIs 

@csrf_exempt
def userSignUp(request):
    response = {}
    if not request.user.is_authenticated:
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                email = data["email"]
                fname = data["fname"]
                lname = data["lname"]
                password = data["password"]
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=fname,
                    last_name=lname
                )
                user.save()
            except Exception as err:
                response["status"] = "failed"
                response["message"] = "Error: " + str(err)
            else:
                response["status"] = "success"
                response["message"] = "Account Created"
    return JsonResponse(response, safe=True)

@csrf_exempt
def userLogin(request):
    response = {}
    if not request.user.is_authenticated:
        if request.method == "POST":
            data = json.loads(request.body)
            email = data["email"]
            password = data["password"]
            user = authenticate(
                username=email,
                password=password
            )
            if user is not None:
                login(request, user)
                response["status"] = "success"
            else:
                response["status"] = "failed"
                response["message"] = "Invalid Credentials!"
    return JsonResponse(response, safe=True)

def userLogout(request):
    logout(request)
    return redirect("/")
