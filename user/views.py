from allauth.socialaccount.models import SocialAccount
from django.contrib import messages
import os
import hashlib
from django.db.models import Q
from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import HttpResponse, redirect, render,get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from home.util import Notification
from home.models import *
from home.views import getSocialAccount, getSocialAccountByUser
from user.forms import *
from user.tokens import *

class loginView(View):
  def get(self, request):
    if (request.user.is_authenticated):
      return redirect("home:index")
    
    notification_temp = request.session.pop('password_reset_notification', None)
    print(notification_temp["title"] if notification_temp else None)
    print(notification_temp["content"] if notification_temp else None)
    print(notification_temp["status"] if notification_temp else None)
    
    form = LoginForm()
    context = {
      "web": "Login",
      "cssFiles": ["/static/user/login.css",
                   ],
      "form": form,
      "notification":Notification(notification_temp["title"],notification_temp["content"],notification_temp["status"]) if notification_temp else None,
    }
    return render(request, 'user/login.html', context)
  
  def post(self, request):
    form = LoginForm(request, data=request.POST)
    context = {
      "web": "Login",
      "cssFiles": ["/static/user/login.css",
                   ],
      "form": form,
    }
    if form.is_valid():
      username = request.POST.get('username')
      password = request.POST.get('password')
      user = authenticate(username=username, password=password)
      if user is None:
        return redirect("user:login")
      else:
        login(request=request, user=user)
        remember_me = request.POST.get('remember_me')
        if not remember_me:
          request.session.set_expiry(0)
        return redirect("home:index")
    else:
      notification = Notification("Login Unsuccessful","Incorrect username or password. Please try again.","error")
      context = {
      "web": "Login",
      "cssFiles": ["/static/user/login.css",
                   ],
      "form": form,
      "notification": notification,
     }
      return render(request, "user/login.html", context)
    

def activate(request, uidb64, token):
  try:
    uid = force_str(urlsafe_base64_decode(uidb64))
    print(uidb64)
    print(uid)
    user = User.objects.get(username = uid)
  except:
    user = None
  print(user.username)
  if user is not None and account_activation_token.check_token(user, token):
    user.is_active = True
    user.save()
    messages.success(request, "Create account successfully. You can log in now.")
  else:
    messages.error(request, "Activation link is invalid")
  return redirect("home:index")


def hash_string(input_string):
  sha256_hash = hashlib.sha256()
  sha256_hash.update(input_string.encode('utf-8'))
  return sha256_hash.hexdigest()

class registerView(View):
  def get(self, request):
    usernames = list(User.objects.values_list('username', flat=True))
    emails = list(User.objects.values_list('email', flat=True))
    
    usernames = [hash_string(username) for username in usernames]
    emails = [hash_string(email) for email in emails]
    
    context = {
      "web": "Register",
      "usernames":usernames,
      "emails":emails,
    }
    return render(request, "user/register.html", context)
  
  def post(self, request):

    email = request.POST.get('Email')

    form_data = {
          'username': request.POST.get('Username'),
          'email': request.POST.get('Email'),
          'password1': request.POST.get('New-password'),
          'password2': request.POST.get('Repeat-new-password'),
          'first_name': request.POST.get('firstname'),
          'last_name': request.POST.get('lastname'),
          'gender':2,
        }

    form = RegisterForm(form_data)
    
    if form.is_valid():
      user = form.save(commit=False)
      user.is_active = False
      user.save()
      print(user.username)
      registerView.activateEmail(request, user, form.cleaned_data.get('email'))
      # user.save()

      notification = Notification("Your account is almost ready","Please check your email to activate your account.","success")
      
      usernames = list(User.objects.values_list('username', flat=True))
      emails = list(User.objects.values_list('email', flat=True))
      context = {
        "web": "Register",
        "usernames":usernames,
        "email":email,
        "emails":emails,
        "notification": notification,
      }
      return render(request, "user/register.html", context)
    else:
      print("Form is invalid. Errors:")
      for field, errors in form.errors.items():
          for error in errors:
              print(f"Error in {field}: {error}")

      usernames = list(User.objects.values_list('username', flat=True))
      emails = list(User.objects.values_list('email', flat=True))
      context = {
        "web": "Register",
        "usernames":usernames,
        "emails":emails,
      }
      return render(request, "user/register.html", context)

  def activateEmail(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string("user/template_activate_account.html", {
      "user": user.username,
      "domain": get_current_site(request),
      "uid": urlsafe_base64_encode(force_bytes(user.username)),
      "token": account_activation_token.make_token(user),
      "protocol": "https" if request.is_secure() else "http"
    })
    print("Username:", user.username)
    print("Code:", urlsafe_base64_encode(force_bytes(user.pk)))
    print("Current site:", get_current_site(request))
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
      messages.success(request, f'Dear <b>{user.username}</b>, please go to your email <b>{to_email}</b>.')
    else:
      messages.error(request, f'Problem sending email to {to_email}, check if you typed correctly')


class signupRedirect(View):
  def get(self, request):
    messages.error(request, "There are errors when logging in.<br> There might already exist an account with this email.")
    return redirect("user:login")


class logoutView(View):
  def get(self, request):
    logout(request=request)
    return redirect("/")


class profileInfoRedirectView(LoginRequiredMixin, View):
  login_url = "user:login"
  def get(self, request):
    return redirect(f"/user/profile/userID={request.user.id}")
  

class profileInfoView(LoginRequiredMixin, View):
  login_url = "user:login"
  
  def get(self, request, id):
    owner = User.objects.get(id = id)
    date_join = str(owner.date_joined.strftime("%d/%m/%Y"))
    date_active = str(owner.last_login.strftime("%d/%m/%Y"))
    
    mod_app_notification = request.session.pop('mod_app_notification', None)
    profile_update_notification = request.session.pop('profile_update_notification', None)
    notification_temp = mod_app_notification or profile_update_notification

    context = {
      "web": "Info",
      "owner": owner,
      "socialAccount": getSocialAccount(request),
      "ownerSocialAccount": getSocialAccountByUser(owner),
      "date_join": date_join,
      "date_active": date_active,
      "notification":Notification(notification_temp["title"],notification_temp["content"],notification_temp["status"]) if notification_temp else None,
    }
    return render(request, "user/profileInfo.html", context)
  
  def post(self, request):
    pass


class profileEditView(LoginRequiredMixin, View):
  login_url = "user:login"
  def get(self, request):
    form = ProfileEditForm(instance=request.user)
    user = User.objects.get(id=request.user.id)
    birthdate = str(user.birthdate)
    context = {
      "web": "Edit profile",
      "cssFiles": [],
      "form": form,
      "socialAccount": getSocialAccount(request),
      "user":user,
      "birthdate":birthdate,
    }
    return render(request, "user/profileEdit.html", context)
  
  def post(self, request):
    
    
  
    form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
    if form.is_valid():
      user = User.objects.get(id=request.user.id)
      cleaned_data = form.cleaned_data
      old_avatar = user.avatar.path if user.avatar else None
      print(old_avatar)
      
 
      user.first_name = cleaned_data['first_name']

      user.last_name = cleaned_data['last_name']

      user.birthdate = cleaned_data['birthdate']

      user.phoneNum = cleaned_data['phoneNum']

      user.address = cleaned_data['address']

      user.gender = cleaned_data['gender']
      if request.FILES.get('avatar'):
        user.avatar = request.FILES['avatar']
        
        
      user.save()
      notification = {
        "title": "Profile modified successfully",
        "content": "Your profile has been updated.",
        "status": "success"
      }  
      messages.success(request, "Profile info updated successfully.")
      request.session['profile_update_notification'] = notification
      if request.FILES.get('avatar') and old_avatar:
        print("Removing old avatar")
        if os.path.exists(old_avatar):
          os.remove(old_avatar)
      return redirect("user:info")
    else:
      context = {
        "web": "Edit profile",
        "cssFiles": [],
        "form": form,
        "socialAccount": getSocialAccount(request),
      }
      return render(request, "user/profileEdit.html", context)
    

class changePasswordView(LoginRequiredMixin, View):
  login_url = "user:login"
  
  def get(self, request):
    form = PasswordChangeForm(request.user)
    context = {
      "web": "Change password",
      "cssFiles": [],
      "form": form,
      "socialAccount": getSocialAccount(request),
    }
    return render(request, "user/passwordChange.html", context)
  
  def post(self, request):

    old_password = request.POST.get("old_password")
    new_password1 = request.POST.get("new_password1")
    new_password2 = request.POST.get("new_password2")

    print(old_password, new_password1, new_password2)

    form = PasswordChangeForm(request.user, request.POST)
    context = {
      "web": "Change password",
      "cssFiles": ["/static/user/passwordChange.css",
                  ],
      "form": form,
      "socialAccount": getSocialAccount(request),
    }
    if form.is_valid():
      notification = Notification("Password Changed Successfully","Your password has been updated successfully. Please use your new password the next time you log in.","success")
      context["notification"] = notification
      user = form.save()
      update_session_auth_hash(request, user)  # Important!
      return render(request, "user/passwordChange.html", context)
    else:
      content = form.errors.as_data()

      if 'old_password' in content:
          content = content["old_password"][0].messages[0]
      elif 'new_password2' in content:
          content = content["new_password2"][0].messages[0]
      else:
          content = "An unknown error occurred."

      notification = Notification("A problem has occured",content,"error")
      context["notification"] = notification
      return render(request, "user/passwordChange.html", context)


class recoverAccountView(auth_views.PasswordResetView):
  success_url = reverse_lazy("user:recover")
  email_template_name = "user/recover/recoverEmail.html"
  template_name = "user/recover/recoverForm.html"
  subject_template_name = "user/recover/recoverEmailSubject.txt"
  
  def form_valid(self, form):
    messages.success(self.request, "email sent")
    return super().form_valid(form)

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['notification'] = Notification(
        "Password recover email sent",
        "If your email is associated with an account, you will get a reset link shortly. Please check your inbox.",
        "info"
    )
    context['web'] = "Recover password"
    return context

class recoverDoneView(auth_views.PasswordResetDoneView):
  template_name = "user/recover/recoverDone.html"


class recoverConfirmView(auth_views.PasswordResetConfirmView):
  success_url=reverse_lazy("user:login")
  template_name = "user/recover/recoverConfirm.html"
  
  def form_valid(self, form):
    # Store the notification data in the session
    notification = {
        "title": "Password reset complete",
        "content": "You can now log in with your new password.",
        "status": "success"
    }
    messages.success(self.request, "Password reset complete")
    self.request.session['password_reset_notification'] = notification
    return super().form_valid(form)

  def get_context_data(self, **kwargs):
    print("run get context data")
    context = super().get_context_data(**kwargs)
    context['uidb64'] = self.kwargs['uidb64']
    context['token'] = self.kwargs['token']
    context['web'] = "Recover password"
    context['notification'] = Notification(
        "Password reset complete",
        "You can now log in with your new password.",
        "success"
    )
    return context


class recoverCompleteView(auth_views.PasswordResetCompleteView):
  template_name = "user/recover/recoverComplete.html"
  login_url = "user:login"
  
  
class userBorrowanceManagerView(LoginRequiredMixin,View):
  login_url = "user:login"
  
  def get(self, request):
    
    borrowancesRequests = Borrowance.objects.filter(userID_id=request.user.id, status=0).select_related(
    'copyID__bookID',  
    'copyID__userID'  
    ).order_by('-borrowDate')
    
    borrowancesBorrowing = Borrowance.objects.filter(userID_id=request.user.id, status=2).select_related(
    'copyID__bookID',
    'copyID__userID'
    ).order_by('-borrowDate')
    
    borrowancesHistory = Borrowance.objects.filter(
        Q(userID_id=request.user.id),
        Q(status=1) | Q(status=3)
    ).select_related('copyID__bookID','copyID__userID').order_by('-borrowDate')
    
    context = {
      "web":"Borrow/Return books",
      "socialAccount": getSocialAccount(request),
      "borrowancesRequests":borrowancesRequests[:5],
      "borrowancesBorrowing":borrowancesBorrowing[:5],  
      "borrowancesHistory":borrowancesHistory[:5],
    }
    
    return render(request, "user/borrowManage.html", context=context)
  
  def post(self, request):
    
    action = request.POST.get("action")
    if action == "delete":
      borrowance = Borrowance.objects.get(id=request.POST.get("borrowanceId"))
      copy = Copy.objects.get(id=borrowance.copyID_id)
      copy.status = 1
      copy.save()
      borrowance.delete()   
        
    if action == "return":
      borrowance = Borrowance.objects.get(id=request.POST.get("borrowanceId"))
      borrowance.status = 3
      borrowance.save()
      
      copy = Copy.objects.get(id=borrowance.copyID_id)
      copy.status = 1
      copy.save()
    return redirect("user:borrow")
  