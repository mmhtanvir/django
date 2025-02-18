from django.shortcuts import render, redirect
from .models import Users
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .models import *


@login_required(login_url='/login/')
def users(request):
    if request.method == 'POST':
        data = request.POST

        user_image = request.FILES.get('user_image')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        Users.objects.create(
            first_name=first_name,
            last_name=last_name,
            user_image=user_image,
        )
        return redirect('/')
    
    print(Users)

    queryset = Users.objects.all()

    if request.GET.get('search'):
        queryset = queryset.filter(first_name__icontains=request.GET.get('search'))

    context = {'users': queryset}
    return render(request, 'index.html', context)

def delete_user(request, id):
    try:
        user = Users.objects.get(id=id)
        user.delete()
        return redirect('/')
    except Users.DoesNotExist:
        return HttpResponse("User not found.", status=404)

def update_user(request, id):
    user = Users.objects.get(id=id)

    if request.method == 'POST':
        data = request.POST

        user_image = request.FILES.get('user_image')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        
        user.first_name = first_name
        user.last_name = last_name

        if user_image:
            user.user_image = user_image

        user.save()
        return redirect('/')
    context = {'user': user}
    return render(request, 'update.html', context)

def login_page(request):
    
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not User.objects.filter(username=username).exists():
            
            messages.error(request, 'Invalid Username')
            return redirect('/login/')
        
        user = authenticate(username=username, password=password)
        
        if user is None:
            messages.error(request, "Invalid Password")
            return redirect('/login/')
        else:
            login(request, user)
            return redirect('/')
    return render(request, 'login.html')

def register_page(request):
    
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = User.objects.filter(username=username)
        
        if user.exists():
            
            messages.info(request, "Username already taken!")
            return redirect('/register/')
        
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username
        )
        
        user.set_password(password)
        user.save()
        
        messages.info(request, "Account created Successfully!")
        return redirect('/login/')
    
    return render(request, 'register.html')

def user_logout(request):
    logout(request)
    return redirect('/') 