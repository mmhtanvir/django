import random
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
import http.client
import mimetypes
from codecs import encode
from .models import Task

def user_login(request):
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

def register(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect('/register/')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered!")
            return redirect('/register/')        
        
        first_name, last_name = name.split(" ", 1) if " " in name else (name, "")

        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=password
        )
        
        messages.success(request, "Account created successfully! You can now log in.")
        return redirect('/login/')
    
    return render(request, 'register.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('/')

@login_required
def home(request):
    tasks = Task.objects.filter(created_by=request.user).order_by('-created_at')
    
    search_query = request.GET.get('search', '')
    if search_query:
        tasks = tasks.filter(task_name__icontains=search_query)

    filter_status = request.GET.get('status', 'all')
    if filter_status == 'complete':
        tasks = tasks.filter(status='Complete')
    elif filter_status == 'incomplete':
        tasks = tasks.filter(status='Incomplete')
    
    return render(request, 'index.html', {'tasks': tasks, 'search_query': search_query, 'filter_status': filter_status})

@login_required
def add_task(request):
    if request.method == 'POST':
        task_name = request.POST.get('task_name')
        due_date = request.POST.get('due_date')
        
        try:
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
            if due_date < datetime.now().date():
                messages.error(request, "Due date must be in the future.")
                return redirect('/')
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
            return redirect('/')
        
        Task.objects.create(
            task_name=task_name,
            due_date=due_date,
            created_by=request.user,
            status='Incomplete'
        )
        
        messages.success(request, "Task added successfully!")
        return redirect('/')
    
    return redirect('/')

@login_required
def update_task(request, task_id):
    if request.method == 'POST':
        task = Task.objects.get(id=task_id, created_by=request.user)
        task.task_name = request.POST.get('task_name')
        task.due_date = request.POST.get('due_date')
        task.status = request.POST.get('status', 'Incomplete')
        task.save()
        
        messages.success(request, "Task updated successfully!")
        return redirect('/')
    
    return redirect('/')

@login_required
def delete_task(request, task_id):
    task = Task.objects.get(id=task_id, created_by=request.user)
    task.delete()
    
    messages.success(request, "Task deleted successfully!")
    return redirect('/')

def send_infobip_email(to_email, otp):
    conn = http.client.HTTPSConnection("rpmq9p.api.infobip.com")
    dataList = []
    boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'
    
    dataList.append(encode('--' + boundary))
    dataList.append(encode('Content-Disposition: form-data; name=from;'))
    dataList.append(encode('Content-Type: {}'.format('text/plain')))
    dataList.append(encode(''))
    dataList.append(encode("mahamudul.hasan.tanvirr@gmail.com"))
    
    dataList.append(encode('--' + boundary))
    dataList.append(encode('Content-Disposition: form-data; name=subject;'))
    dataList.append(encode('Content-Type: {}'.format('text/plain')))
    dataList.append(encode(''))
    dataList.append(encode("Your OTP for Password Reset"))
    
    dataList.append(encode('--' + boundary))
    dataList.append(encode('Content-Disposition: form-data; name=to;'))
    dataList.append(encode('Content-Type: {}'.format('text/plain')))
    dataList.append(encode(''))
    dataList.append(encode("{\"to\":\"" + to_email + "\",\"placeholders\":{\"otp\":\"" + str(otp) + "\"}}"))
    
    dataList.append(encode('--' + boundary))
    dataList.append(encode('Content-Disposition: form-data; name=text;'))
    dataList.append(encode('Content-Type: {}'.format('text/plain')))
    dataList.append(encode(''))
    dataList.append(encode("Your OTP is: {{otp}}. Please use it to reset your password."))
    
    dataList.append(encode('--' + boundary + '--'))
    dataList.append(encode(''))
    
    body = b'\r\n'.join(dataList)
    payload = body
        
    headers = {
        'Authorization': 'App f2706fe81ee6b005f2a2431b5a726ff5-b4cb3a8d-5e2f-4968-89df-da06393922d0',
        'Content-Type': 'multipart/form-data; boundary={}'.format(boundary),
        'Accept': 'application/json',
    }

    conn.request("POST", "/email/3/send", payload, headers)
    res = conn.getresponse()
    data = res.read()
    
    print("Infobip Response:", data.decode("utf-8"))
    
    return data.decode("utf-8")

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp_entered = request.POST.get('otp')
        new_password = request.POST.get('new_password')

        if not otp_entered and not new_password:
            user = User.objects.filter(email=email).first()
            if user:
                otp = random.randint(100000, 999999)
                if send_infobip_email(email, otp):
                    print(otp)
                    request.session['otp'] = otp
                    request.session['email'] = email
                    messages.success(request, "OTP sent successfully! Check your email.")
                    return render(request, 'pass_forgot.html', {'step': 'otp'})
                else:
                    messages.error(request, "Failed to send OTP. Please try again.")
            else:
                messages.error(request, "Email not found.")
            return render(request, 'pass_forgot.html')

        if otp_entered and not new_password:
            stored_otp = request.session.get('otp')
            if otp_entered == str(stored_otp):
                messages.success(request, "OTP verified. Please set a new password.")
                return render(request, 'pass_forgot.html', {'step': 'reset'})
            else:
                messages.error(request, "Invalid OTP entered. Please try again.")
                return render(request, 'pass_forgot.html', {'step': 'otp'})

        if new_password:
            user = User.objects.get(email=request.session.get('email'))
            user.set_password(new_password)
            user.save()
            messages.success(request, "Your password has been reset successfully.")
            return redirect('/login/')

    return render(request, 'pass_forgot.html')