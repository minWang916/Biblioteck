from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import HttpResponse, redirect, render
from django.views import View
from home.functions import *
from home.models import *


class ControlView(LoginRequiredMixin, View):
  login_url = "user:login"  # URL to redirect to if the user is not logged in

  def get(self, request):
      # Check if the logged-in user is an admin
      if not (request.user.role == 2):
          # Display an error message if the user is not authorized
          messages.error(request, "You are not allowed to access")
          # Redirect to the home page
          return redirect("home:index")

      # Query all users from the User model
      persons = User.objects.all()
      # Prepare the context to be passed to the template
      context = {
          "web": "Control",  # Page title
          "cssFiles": [],  # List of CSS files to be included
          "jsFiles": [],  # List of JS files to be included
          "persons": persons,  # List of all users
      }
      # Render the template with the context
      return render(request, "control/control.html", context)
  
  def post(self, request):
      # Handler for HTTP POST requests (currently not implemented)
      pass

class ModReviewView(LoginRequiredMixin, View):
  login_url = "user:login"  # URL to redirect if user is not logged in
  template_url = "control/review/modReview.html"  # Template file to render for this view

  def get(self, request):
      # Handler for HTTP GET requests

      # Check if the logged-in user has role 2 (assuming role 2 means admin or moderator)
      if not (request.user.role == 2):
          messages.error(request, "You are not allowed to access")  # Display error message if not authorized
          return redirect("home:index")  # Redirect to home:index if not authorized

      # Query all mod applications
      applications = ModApplication.objects.all()

      # Prepare context dictionary with data to pass to the template
      context = {
          "web": "Mod Review",  # Title for the page
          "applications": applications,  # Queryset of all mod applications
          "socialAccount": getSocialAccount(request),  # Data from getSocialAccount function
      }

      # Render the template with context data and return the rendered response
      return render(request, self.template_url, context)

  def post(self, request):
      # Handler for HTTP POST requests (currently not implemented)
      pass


class BookReviewView(LoginRequiredMixin, View):
  login_url = "user:login"  # URL to redirect if user is not logged in
  template_url = "control/review/bookReview.html"  # Template file to render for this view

  def get(self, request):
    # Handler for HTTP GET requests

    # Check if the logged-in user is an admin
    if not (request.user.role == 2):
        messages.error(request, "You are not allowed to access")  # Display error message if not authorized
        return redirect("home:index")  # Redirect to home:index if not authorized

    # Query all books with status 0 (pending review)
    books = Book.objects.filter(status=0)

    # Prepare context dictionary with data to pass to the template
    context = {
        "web": "Book Review",  # Title for the page
        "books": books,  # Query set of books pending review
        "socialAccount": getSocialAccount(request),  # Data from getSocialAccount function
    }

    # Render the template with context data and return the rendered response
    return render(request, self.template_url, context)

  def post(self, request):
    # Handler for HTTP POST requests (currently not implemented)
    pass

class BookDecideView(LoginRequiredMixin, View):
  login_url = "user:login"  # URL to redirect if user is not logged in

  def get(self, request, id):
      # Handler for HTTP GET requests
      pass

  def post(self, request, action, bookid):
      # Handler for HTTP POST requests
      
      # Check if the logged-in user has role 2 (assuming role 2 means admin or moderator)
      if not (request.user.role == 2):
          messages.error(request, "You are not allowed to access")  # Display error message if not authorized
          return redirect("home:index")  # Redirect to home:index if not authorized
      
      # Check the action parameter to determine whether to approve or decline the book
      if action == "approve":
          # If the action is to approve, find the book by its id and set its status to 1 (approved)
          book = Book.objects.get(id=bookid)
          book.status = 1
          book.save()  # Save the updated book status to the database
      elif action == "decline":
          # If the action is to decline, find the book by its id and set its status to 2 (declined)
          book = Book.objects.get(id=bookid)
          book.status = 2
          book.save()  # Save the updated book status to the database
      else:
          # If the action parameter is neither "approve" nor "decline", display an error message
          messages.error(request, "There is an error")
      
      # Redirect to the admin management page after processing the action
      return redirect("mod:adminManage")

class ModDecideView(LoginRequiredMixin, View):
  login_url = "user:login"  # URL to redirect to if the user is not logged in

  def get(self, request, id):
      # Handler for HTTP GET requests (currently not implemented)
      pass

  def post(self, request, action, userid):
      # Handler for HTTP POST requests
      
      # Check if the logged-in user has role 2 (assuming role 2 means admin or moderator)
      if not (request.user.role == 2):
          messages.error(request, "You are not allowed to access")  # Display error message if not authorized
          return redirect("home:index")  # Redirect to home:index if not authorized
      
      # Check the action parameter to determine whether to approve or decline the application
      if action == "approve":
          # If the action is to approve, find the ModApplication by its id and set its status to 1 (approved)
          application = ModApplication.objects.get(id=userid)
          application.status = 1
          # Find the applicant (user) associated with the application and set their role to 1 (moderator)
          applicant = User.objects.get(id=application.applicant.id)
          applicant.role = 1
          # Save the updated application and applicant to the database
          application.save()
          applicant.save()
      elif action == "decline":
          # If the action is to decline, find the ModApplication by its id and set its status to 2 (declined)
          application = ModApplication.objects.get(id=userid)
          application.status = 2
          application.save()  # Save the updated application to the database
      else:
          # If the action parameter is neither "approve" nor "decline", display an error message
          messages.error(request, "There is an error")
      
      # Redirect to the admin management page after processing the action
      return redirect("mod:adminManage")

    
