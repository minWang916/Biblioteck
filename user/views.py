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
      return redirect("home:index") # Redirects to the home page
    
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
      # Constructs a Notification object for login failure
      notification = Notification("Login Unsuccessful","Incorrect username or password. Please try again.","error")
      context = {
      "web": "Login",
      "cssFiles": ["/static/user/login.css",
                  ],
      "form": form,
      "notification": notification, # Adds the notification to the context
      }
      return render(request, "user/login.html", context)
    

def activate(request, uidb64, token):
  try:
    uid = force_str(urlsafe_base64_decode(uidb64))
    print(uidb64)
    print(uid)
    user = User.objects.get(username = uid) # Retrieve the user based on the decoded username
  except:
    user = None
  print(user.username)
  if user is not None and account_activation_token.check_token(user, token):
    # If the user exists and the token is valid, activate the user account
    user.is_active = True
    user.save()
    messages.success(request, "Create account successfully. You can log in now.")
  else:
    messages.error(request, "Activation link is invalid")
  return redirect("home:index") # Redirect to the home page after activation


def hash_string(input_string):
  sha256_hash = hashlib.sha256()  # Create a new SHA-256 hash object
  sha256_hash.update(input_string.encode('utf-8'))  # Update the hash object with the bytes of the input string
  return sha256_hash.hexdigest()  # Return the hexadecimal digest of the hash

class registerView(View):
    def get(self, request):
        # Get lists of all usernames and emails from the database
        usernames = list(User.objects.values_list('username', flat=True))
        emails = list(User.objects.values_list('email', flat=True))
        
        # Hash the usernames and emails
        usernames_hashed = [hash_string(username) for username in usernames]
        emails_hashed = [hash_string(email) for email in emails]
        
        # Prepare the context for rendering the registration page
        context = {
            "web": "Register",
            "usernames": usernames_hashed,
            "emails": emails_hashed,
        }
        # Render the registration page with the context
        return render(request, "user/register.html", context)
    
    def post(self, request):
        # Get the email from the POST request
        email = request.POST.get('Email')
        
        # Gather all form data into a dictionary
        form_data = {
            'username': request.POST.get('Username'),
            'email': request.POST.get('Email'),
            'password1': request.POST.get('New-password'),
            'password2': request.POST.get('Repeat-new-password'),
            'first_name': request.POST.get('firstname'),
            'last_name': request.POST.get('lastname'),
            'gender': 2,  # Assuming 2 represents a default or unknown gender
        }
        
        # Create a RegisterForm instance with the form data
        form = RegisterForm(form_data)
        
        # Check if the form is valid
        if form.is_valid():
            # Save the user but don't commit to the database yet
            user = form.save(commit=False)
            user.is_active = False  # Set the user as inactive until email verification
            user.save()  # Save the user to the database
            
            # Call the method to send an activation email
            self.activateEmail(request, user, form.cleaned_data.get('email'))
            
            # Create a success notification
            notification = Notification("Your account is almost ready", "Please check your email to activate your account.", "success")
            
            # Get hashed usernames and emails for the context
            usernames = list(User.objects.values_list('username', flat=True))
            emails = list(User.objects.values_list('email', flat=True))
            usernames_hashed = [hash_string(username) for username in usernames]
            emails_hashed = [hash_string(email) for email in emails]
            
            # Prepare the context with the notification
            context = {
                "web": "Register",
                "usernames": usernames_hashed,
                "emails": emails_hashed,
                "notification": notification,
            }
            # Render the registration page with the context and notification
            return render(request, "user/register.html", context)
        else:
            # Print form errors for debugging
            print("Form is invalid. Errors:")
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Error in {field}: {error}")

            # Get hashed usernames and emails for the context
            usernames = list(User.objects.values_list('username', flat=True))
            emails = list(User.objects.values_list('email', flat=True))
            usernames_hashed = [hash_string(username) for username in usernames]
            emails_hashed = [hash_string(email) for email in emails]
            
            # Prepare the context with the form errors
            context = {
                "web": "Register",
                "usernames": usernames_hashed,
                "emails": emails_hashed,
            }
            # Render the registration page with the context
            return render(request, "user/register.html", context)

    # Method to send an activation email
    def activateEmail(self, request, user, to_email):
        # Define the subject of the email
        mail_subject = "Activate your user account."
        # Render the email message using a template
        message = render_to_string("user/template_activate_account.html", {
            "user": user.username,
            "domain": get_current_site(request),  # Get the current site domain
            "uid": urlsafe_base64_encode(force_bytes(user.username)),  # Encode the user ID
            "token": account_activation_token.make_token(user),  # Generate the activation token
            "protocol": "https" if request.is_secure() else "http"  # Determine the protocol
        })
        
        # Create an email message
        email = EmailMessage(mail_subject, message, to=[to_email])
        # Try to send the email and provide user feedback
        if email.send():
            messages.success(request, f'Dear <b>{user.username}</b>, please go to your email <b>{to_email}</b>.')
        else:
            messages.error(request, f'Problem sending email to {to_email}, check if you typed correctly.')

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
      # Get the email from the POST request
      email = request.POST.get('Email')

      # Gather all form data into a dictionary
      form_data = {
            'username': request.POST.get('Username'),
            'email': request.POST.get('Email'),
            'password1': request.POST.get('New-password'),
            'password2': request.POST.get('Repeat-new-password'),
            'first_name': request.POST.get('firstname'),
            'last_name': request.POST.get('lastname'),
            'gender':2,
          }
      
      # Create a RegisterForm instance with the form data
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

    # Method to send an activation email
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
  # Specify the URL to redirect to for login
  login_url = "user:login"

  def get(self, request, id):
    # Fetch the user based on the provided ID
    owner = User.objects.get(id=id)
    # Format the user's date joined and last login date as strings
    date_join = str(owner.date_joined.strftime("%d/%m/%Y"))
    date_active = str(owner.last_login.strftime("%d/%m/%Y"))
    
    # Attempt to retrieve and pop any notifications from the session
    mod_app_notification = request.session.pop('mod_app_notification', None)
    profile_update_notification = request.session.pop('profile_update_notification', None)
    # Use whichever notification is available (mod_app or profile_update)
    notification_temp = mod_app_notification or profile_update_notification

    # Prepare the context for rendering the profile info page
    context = {
        "web": "Info",
        "owner": owner,  # The profile owner
        "socialAccount": getSocialAccount(request),  # Social account of the current user
        "ownerSocialAccount": getSocialAccountByUser(owner),  # Social account of the profile owner
        "date_join": date_join,  # Formatted date joined
        "date_active": date_active,  # Formatted last login date
        # Notification object if there is any notification data available
        "notification": Notification(notification_temp["title"], notification_temp["content"], notification_temp["status"]) if notification_temp else None,
    }
    # Render the profile info page with the context
    return render(request, "user/profileInfo.html", context)

  def post(self, request):
    # The post method is defined but not implemented
    pass


class profileEditView(LoginRequiredMixin, View):
  # Specify the URL to redirect to for login
  login_url = "user:login"

  def get(self, request):
    # Initialize the profile edit form with the current user's data
    form = ProfileEditForm(instance=request.user)
    # Get the current user's information
    user = User.objects.get(id=request.user.id)
    # Format the user's birthdate as a string
    birthdate = str(user.birthdate)
    
    # Prepare the context for rendering the profile edit page
    context = {
        "web": "Edit profile",
        "cssFiles": [],  # List of CSS files to be included
        "form": form,  # The profile edit form
        "socialAccount": getSocialAccount(request),  # Social account information of the current user
        "user": user,  # The current user's information
        "birthdate": birthdate,  # Formatted birthdate
    }
    # Render the profile edit page with the provided context
    return render(request, "user/profileEdit.html", context)

  def post(self, request):
    # Initialize the profile edit form with the submitted data and files
    form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
    
    if form.is_valid():
      # Get the current user's information
      user = User.objects.get(id=request.user.id)
      # Extract cleaned data from the form
      cleaned_data = form.cleaned_data
      # Get the path of the old avatar if it exists
      old_avatar = user.avatar.path if user.avatar else None
      print(old_avatar)
      
      # Update the user's information with the cleaned data from the form
      user.first_name = cleaned_data['first_name']
      user.last_name = cleaned_data['last_name']
      user.birthdate = cleaned_data['birthdate']
      user.phoneNum = cleaned_data['phoneNum']
      user.address = cleaned_data['address']
      user.gender = cleaned_data['gender']
      
      # Update the user's avatar if a new one is uploaded
      if request.FILES.get('avatar'):
          user.avatar = request.FILES['avatar']
      
      # Save the updated user information
      user.save()
      
      # Prepare a success notification
      notification = {
          "title": "Profile modified successfully",
          "content": "Your profile has been updated.",
          "status": "success"
      }
      messages.success(request, "Profile info updated successfully.")
      # Store the notification in the session
      request.session['profile_update_notification'] = notification
      
      # Remove the old avatar if a new one is uploaded and the old avatar exists
      if request.FILES.get('avatar') and old_avatar:
          print("Removing old avatar")
          if os.path.exists(old_avatar):
              os.remove(old_avatar)
      
      # Redirect to the user's profile info page
      return redirect("user:info")
    else:
      # Prepare the context for re-rendering the profile edit page with the form errors
      context = {
          "web": "Edit profile",
          "cssFiles": [],
          "form": form,  # The form with errors
          "socialAccount": getSocialAccount(request),  # Social account information of the current user
      }
      # Render the profile edit page with the provided context
      return render(request, "user/profileEdit.html", context)

class changePasswordView(LoginRequiredMixin, View):
  # Specify the URL to redirect to for login if the user is not authenticated
  login_url = "user:login"
  
  def get(self, request):
    # Initialize the password change form with the current user's data
    form = PasswordChangeForm(request.user)
    # Prepare the context for rendering the password change page
    context = {
        "web": "Change password",  # Page title
        "cssFiles": [],  # List of CSS files to be included
        "form": form,  # The password change form
        "socialAccount": getSocialAccount(request),  # Social account information of the current user
    }
    # Render the password change page with the provided context
    return render(request, "user/passwordChange.html", context)
  
  def post(self, request):
    # Get the old and new passwords from the POST data
    old_password = request.POST.get("old_password")
    new_password1 = request.POST.get("new_password1")
    new_password2 = request.POST.get("new_password2")

    # Print the passwords for debugging purposes
    print(old_password, new_password1, new_password2)

    # Initialize the password change form with the submitted data
    form = PasswordChangeForm(request.user, request.POST)
    # Prepare the context for re-rendering the password change page
    context = {
        "web": "Change password",  # Page title
        "cssFiles": ["/static/user/passwordChange.css"],  # List of CSS files to be included
        "form": form,  # The password change form
        "socialAccount": getSocialAccount(request),  # Social account information of the current user
    }
    
    if form.is_valid():
      # Prepare a success notification
      notification = Notification(
          "Password Changed Successfully",
          "Your password has been updated successfully. Please use your new password the next time you log in.",
          "success"
      )
      context["notification"] = notification
      # Save the new password and update the session
      user = form.save()
      update_session_auth_hash(request, user)  # Important to keep the user logged in
      # Render the password change page with the success notification
      return render(request, "user/passwordChange.html", context)
    
    else:
      # Get the form errors
      content = form.errors.as_data()

      # Check for specific error messages
      if 'old_password' in content:
          content = content["old_password"][0].messages[0]
      elif 'new_password2' in content:
          content = content["new_password2"][0].messages[0]
      else:
          content = "An unknown error occurred."

      # Prepare an error notification
      notification = Notification("A problem has occurred", content, "error")
      context["notification"] = notification
      # Render the password change page with the error notification
      return render(request, "user/passwordChange.html", context)

class recoverAccountView(auth_views.PasswordResetView):
  # URL to redirect to after a successful password reset request
  success_url = reverse_lazy("user:recover")
  # Template for the password reset email
  email_template_name = "user/recover/recoverEmail.html"
  # Template for the password reset form
  template_name = "user/recover/recoverForm.html"
  # Template for the email subject
  subject_template_name = "user/recover/recoverEmailSubject.txt"
  
  def form_valid(self, form):
      # Add a success message when the form is valid
      messages.success(self.request, "email sent")
      return super().form_valid(form)

  def get_context_data(self, **kwargs):
      # Get the context data from the parent class
      context = super().get_context_data(**kwargs)
      # Add a notification to the context
      context['notification'] = Notification(
          "Password recover email sent",
          "If your email is associated with an account, you will get a reset link shortly. Please check your inbox.",
          "info"
      )
      context['web'] = "Recover password"  # Page title
      return context

class recoverDoneView(auth_views.PasswordResetDoneView):
  # Template for the password reset done page
  template_name = "user/recover/recoverDone.html"


class recoverConfirmView(auth_views.PasswordResetConfirmView):
  # URL to redirect to after a successful password reset
  success_url = reverse_lazy("user:login")
  # Template for the password reset confirmation form
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
    # Print a message for debugging
    print("run get context data")
    # Get the context data from the parent class
    context = super().get_context_data(**kwargs)
    # Add additional data to the context
    context['uidb64'] = self.kwargs['uidb64']
    context['token'] = self.kwargs['token']
    context['web'] = "Recover password"  # Page title
    context['notification'] = Notification(
        "Password reset complete",
        "You can now log in with your new password.",
        "success"
    )
    return context


class recoverCompleteView(auth_views.PasswordResetCompleteView):
  # Template for the password reset complete page
  template_name = "user/recover/recoverComplete.html"
  # URL to redirect to for login
  login_url = "user:login"
  
  
class userBorrowanceManagerView(LoginRequiredMixin,View):
  # URL to redirect to for login if the user is not authenticated
  login_url = "user:login"
  
  def get(self, request):
    # Get the borrowance requests for the current user
    borrowancesRequests = Borrowance.objects.filter(userID_id=request.user.id, status=0).select_related(
        'copyID__bookID',
        'copyID__userID'
    ).order_by('-borrowDate')
    
    # Get the borrowances that the user is currently borrowing
    borrowancesBorrowing = Borrowance.objects.filter(userID_id=request.user.id, status=2).select_related(
        'copyID__bookID',
        'copyID__userID'
    ).order_by('-borrowDate')
    
    # Get the borrowance history for the current user
    borrowancesHistory = Borrowance.objects.filter(
        Q(userID_id=request.user.id),
        Q(status=1) | Q(status=3)
    ).select_related('copyID__bookID', 'copyID__userID').order_by('-borrowDate')
    
    # Prepare the context for rendering the borrowance management page
    context = {
        "web": "Borrow/Return books",  # Page title
        "socialAccount": getSocialAccount(request),  # Social account information of the current user
        "borrowancesRequests": borrowancesRequests[:5],  # Top 5 borrowance requests
        "borrowancesBorrowing": borrowancesBorrowing[:5],  # Top 5 borrowances being borrowed
        "borrowancesHistory": borrowancesHistory[:5],  # Top 5 borrowance history records
    }
    
    # Render the borrowance management page with the provided context
    return render(request, "user/borrowManage.html", context=context)
  
  def post(self, request):
    # Get the action from the POST data
    action = request.POST.get("action")
    if action == "delete":
        # If the action is to delete, get the borrowance and delete it, and update the copy status
        borrowance = Borrowance.objects.get(id=request.POST.get("borrowanceId"))
        copy = Copy.objects.get(id=borrowance.copyID_id)
        copy.status = 1
        copy.save()
        borrowance.delete()
    
    if action == "return":
        # If the action is to return, update the borrowance and copy status
        borrowance = Borrowance.objects.get(id=request.POST.get("borrowanceId"))
        borrowance.status = 3
        borrowance.save()
        
        copy = Copy.objects.get(id=borrowance.copyID_id)
        copy.status = 1
        copy.save()
    
    # Redirect to the borrowance management page
    return redirect("user:borrow")
  