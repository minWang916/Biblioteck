from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from home.models import *
from home.functions import *

class ControlView(LoginRequiredMixin, View):
  login_url = "user:login"

  def get(self, request):
    if not (request.user.role == 2):
      messages.error(request, "You are not allowed to access")
      return redirect("home:index")
    persons = User.objects.all()
    context = {
      "web": "Control",
      "cssFiles": [],
      "jsFiles": [],
      "persons": persons,
    }
    return render(request, "control/control.html", context)
  
  def post(self, request):
    pass

class ModReviewView(LoginRequiredMixin, View):
  login_url = "user:login"
  template_url = "control/review/modReview.html"

  def get(self, request):
    if not (request.user.role == 2):
      messages.error(request, "You are not allowed to access")
      return redirect("home:index")
    context = {
      "web": "Mod Review",
      "applications": ModApplication.objects.all(),
      "socialAccount": getSocialAccount(request),
    }
    return render(request, self.template_url, context)
  
  def post(self, request):
    pass

class BookReviewView(LoginRequiredMixin, View):
  login_url = "user:login"
  template_url = "control/review/bookReview.html"

  def get(self, request):
    if not (request.user.role == 2):
      messages.error(request, "You are not allowed to access")
      return redirect("home:index")
    context = {
      "web": "Book Review",
      "books": Book.objects.filter(status = 0),
      "socialAccount": getSocialAccount(request),
    }
    return render(request, self.template_url, context)

  def post(self, request):
    pass

class BookDecideView(LoginRequiredMixin, View):
  login_url = "user:login"

  def get(self, request, id):
    pass

  def post(self, request, action, bookid):
    if not (request.user.role == 2):
      messages.error(request, "You are not allowed to access")
      return redirect("home:index")
    if (action == "approve"):
      book = Book.objects.get(id = bookid)
      book.status = 1
      book.save()
    elif (action == "decline"):
      Book.objects.get(id = bookid).status = 2
      book.status = 2
      book.save()
    else:
      messages.error("There is an error")
    return redirect("mod:adminManage")

class ModDecideView(LoginRequiredMixin, View):
  login_url = "user:login"

  def get(self, request, id):
    pass

  def post(self, request, action, userid):
    if not (request.user.role == 2):
      messages.error(request, "You are not allowed to access")
      return redirect("home:index")
    if (action == "approve"):
      application = ModApplication.objects.get(id = userid)
      application.status = 1
      applicant = User.objects.get(id = application.applicant.id)
      applicant.role = 1
      application.save()
      applicant.save()
    elif (action == "decline"):
      application = ModApplication.objects.get(id = userid)
      application.status = 2
      application.save()
    else:
      messages.error("There is an error")
    return redirect("mod:adminManage")

      
    