from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from django.contrib.auth import authenticate,login,logout
from .helpers import send_forget_password_mail
from django.utils import timezone
from .forms import UserUpdateForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

def Login(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            if not username or not password:
                messages.success(request, 'Both Username and Password are required.')
                return redirect('/login/')
            user_obj = User.objects.filter(username = username).first()
            if user_obj is None:
                messages.success(request, 'User not found.')
                return redirect('/login/')
        
        
            user = authenticate(username = username , password = password)
            
            if user is None:
                messages.success(request, 'Wrong password.')
                return redirect('/login/')
        
            login(request , user)
            return redirect('/')

                
            
            
    except Exception as e:
        print(e)
    return render(request , 'login.html')



def Register(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')

        try:
            if User.objects.filter(username = username).first():
                messages.success(request, 'Username is taken.')
                return redirect('/register/')

            if User.objects.filter(email = email).first():
                messages.success(request, 'Email is taken.')
                return redirect('/register/')
            
            user_obj = User(username = username , email = email)
            user_obj.set_password(password)
            user_obj.save()
    
            profile_obj = Profile.objects.create(user = user_obj )
            profile_obj.save()
            return redirect('/login/')

        except Exception as e:
            print(e)

    except Exception as e:
            print(e)

    return render(request , 'register.html')


def Logout(request):
    logout(request)
    return redirect('/')


@login_required(login_url='/login/')
def Home(request):
    return render(request , 'home.html')



def ChangePassword(request , token):
    context = {}
    
    
    try:
        profile_obj = Profile.objects.filter(forget_password_token = token).first()
                # Check if the profile with the token exists
        if profile_obj is None:
            return render(request, "auth/fail_url.html")
            
        
        context = {'user_id' : profile_obj.user.id}
        
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('reconfirm_password')
            user_id = request.POST.get('user_id')
            
            if user_id is  None:
                messages.success(request, 'No user id found.')
                return redirect(f'/accounts/change-password/{token}/')
                
            
            if  new_password != confirm_password:
                messages.success(request, 'Passwords do not match.')
                return redirect(f'/accounts/change-password/{token}/')
                         
            
            user_obj = User.objects.get(id = user_id)
            user_obj.set_password(new_password)
            user_obj.save()
            return render(request, "auth/new_login.html", context={"msg": "Password Changed Successfully!", "s": "success", "d": "success"})

            
            

        
        
    except Exception as e:
        print(e)
    return render(request , 'auth/new_password_reset_confirm.html' , context)


import uuid
def ForgetPassword(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            
            if not User.objects.filter(email=email).first():
                messages.success(request, 'Email not found with this email.')
                return redirect('forget_password')
            
            user_obj = User.objects.filter(email = email).first()
            token = str(uuid.uuid4())
            profile_obj= Profile.objects.filter(user = user_obj).first()
            profile_obj.forget_password_token = token
            profile_obj.save()
            send_forget_password_mail(user_obj.email , token, request)
            # messages.success(request, 'An email is sent.')
            # return redirect('/accounts/forget-password/')
            return render(request, 'auth/new_reset_password_done.html')
    
    
    except Exception as e:
        print(e)
    return render(request , 'auth/new_password_reset.html')



@login_required(login_url='/login/')
def user_update(request):
    user_form = UserUpdateForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)

    if request.method == 'POST':
        if 'user_form_submit' in request.POST:  # User Update Form Submission
            user_form = UserUpdateForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Your account information has been updated!')
                return redirect('profile')

        if 'password_form_submit' in request.POST:  # Password Change Form Submission
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Maintain the user's session after password change
                messages.success(request, 'Your password has been changed!')
                return redirect('profile')

    context = {
        'user_form': user_form,
        'password_form': password_form,
    }
    
    return render(request, 'dashboard/profile.html', context)
