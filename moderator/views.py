from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.views import View
from django.contrib import messages
from .forms import BookForm, CopyForm, ModApplicationForm
from django.core.mail import EmailMessage
from home.models import *
from home.functions import *
from home.util import *
from datetime import date
import csv
import sqlite3
from django.db import connections

# Create your views here.
class modView(LoginRequiredMixin, View):
  login_url = "user:login"
  def get(self, request):
    return HttpResponse('Moderator page')
  
  def post(self, request):
    pass


class addBookView(LoginRequiredMixin, View):
  login_url = "user:login"

  def get(self, request):
    if (request.user.is_authenticated and request.user.role > 0):
      form = BookForm(initial={"status": 1})
      context = {
        "web": "Add Book",
        "cssFiles": [],
        "jsFiles": ["/static/mod/addBook.js",
                  ],
        "form": form,
      }
      return render(request, 'mod/addBook.html', context)
    else:
      messages.error(request, "You don't have the right to add book.")
      return redirect("home:index")

  def post(self, request):
    data = request.POST.dict()
    if (request.user.role > 1):
      data["status"] = 1
    else:
      data["status"] = 0
    form = BookForm(data, request.FILES)
    context = {
      "web": "Add Copy",
      "cssFiles": [],
      "jsFiles": ["/static/mod/addBook.js",
                  ],
      "form": form,
    }
    if form.is_valid():
      print(form.cleaned_data)
      newBook = form.save()
      if (request.user.role == 2):
        messages.success(request, 'Your book has been added')
      else:
        messages.info(request, "Your book will need approval from admin before added.")
        
        BookApplication.objects.create(
          bookID=newBook,
          uploader=request.user,
          status=0,
          created_at=timezone.now(),
        )
        
      return redirect("home:gallery")
    else:
      print(form.cleaned_data)
      notification = Notification("Action failed","Your form is not valid.","error")
      context["notification"] = notification
      return render(request, 'mod/addBook.html', context)


class addCopyView(LoginRequiredMixin, View):
  login_url = "user:login"

  def get(self, request, id):
    if not (request.user.is_authenticated and request.user.role >= 1):
      messages.error(request, "You don't have the right to add copy.")
      return redirect("home:index")
    book = Book.objects.get(id = id)
    form = CopyForm(initial={"bookID": book,
                             "userID": request.user,
                             "regDate": date.today()})
    copies = Copy.objects.filter(bookID = book.id)
    context = {
      "web": "Add Copy",
      "cssFiles": [],
      "book": book,
      "form": form,
      "copies":copies,
    }
    return render(request, 'mod/addCopy.html', context)
  
  def post(self, request, id):
    if not (request.user.is_authenticated and request.user.role >= 1):
      messages.error(request, "You don't have the right to add copy.")
      return redirect("home:index")
    book = Book.objects.get(id = id)
    data = {
      "bookID": book,
      "userID": request.user,
      "regDate": date.today(),
      "note": request.POST.get('note'),
      "status": 1
    }
    form = CopyForm(data)
    if form.is_valid():
      form.save()
      messages.success(request, "Your copy has been added successfully.")
      return redirect("home:book", id)
    else:
      context = {
        "web": "Add Copy",
        "cssFiles": [],
        "book": book,
        "form": form,
      }
      messages.error(request, "There is a problem with adding your copy.")
      return render(request, 'mod/addCopy.html', context)
    

class editBookView(LoginRequiredMixin, View):
  login_url = "user:login"

  def get(self, request, id):
    if not(request.user.is_authenticated and request.user.role >= 1):
      messages.error(request, "You don't have the right to edit book.")
      return redirect("home:index")
    book = Book.objects.get(id = id)
    form = BookForm(instance=book)
    context = {
      "web": "Edit Book",
      "cssFiles": [],
      "book": book,
      "form": form,
    }
    return render(request, "mod/editBook.html", context)

  def post(self, request, id):
    print("POST to edit book", id)
    if not(request.user.is_authenticated and request.user.role >= 1):
      messages.error(request, "You don't have the right to edit book.")
      return redirect("home:index")
    book = Book.objects.get(id = id)
    data = request.POST.dict()
    data["status"] = book.status
    form = BookForm(data, request.FILES, instance=book)
    if form.is_valid():
      print("valid")
      form.save()
      messages.success(request, "The book has been edited succesfully.")
      return redirect("mod:addCopy", id)
    else:
      print("invalid")
      context = {
        "web": "Edit Book",
        "cssFiles": [],
        "book": book,
        "form": form,
      }
      return render(request, "mod/editBook.html", context)
    

class editCopyView(LoginRequiredMixin, View):
  login_url = "user:login"

  def get(self, request, id):
    copy = Copy.objects.get(id = id)
    if not(request.user.is_authenticated and request.user.role >= 1
           and request.user == copy.userID):
      messages.error(request, "You don't have the right to edit copy.")
      return redirect("home:index")
    form = CopyForm(instance=copy)
    context = {
      "web": "Edit Book",
      "cssFiles": [],
      "copy": copy,
      "form": form,
    }
    return render(request, "mod/editCopy.html", context)

  def post(self, request, id):
    if not(request.user.is_authenticated and request.user.role >= 1):
      messages.error(request, "You don't have the right to edit book.")
      return redirect("home:index")
    copy = Copy.objects.get(id = id)
    print(request.POST.get("note"))
    data = {
      "userID": copy.userID,
      "bookID": copy.bookID,
      "status": request.POST.get("status"),
      "note": request.POST.get("note"),
      "regDate": copy.regDate,
    }
    form = CopyForm(data, instance=copy)
    context = {
      "web": "Edit Book",
      "cssFiles": [],
      "copy": copy,
      "form": form,
    }
    if form.is_valid():
      form.save()
      messages.success(request, "The copy has been edited succesfully.")
      return redirect("mod:editCopy", id)
    else:
      return render(request, "mod/editCopy.html", context)


class applyModView(LoginRequiredMixin, View):
  login_url = "user:login"

  def get(self, request):
    if (request.user.role > 0):
      messages.warning(request, "You are already a moderator.")
      return redirect("home:index")
    form = ModApplicationForm(
      initial={
        "applicant": request.user,
        "status": 0,
        "created_at": timezone.now(),
      }
    )
    context = {
      "web": "Mod Apply",
      "form": form,
      "socialAccount": getSocialAccount(request),
    }
    return render(request, "mod/modApply.html", context)

  def post(self, request):
    if (request.user.role > 0):
      messages.warning(request, "You are already a moderator.")
      return redirect("home:index")
    
    userprofile = User.objects.get(id = request.user.id)
    userprofile.phoneNum = request.POST.get("phone")
    userprofile.address = request.POST.get("address")
    userprofile.availableWorkingHours = request.POST.get("working_hours")
    userprofile.description = request.POST.get("description")
    userprofile.save()
    
    data = {
      "applicant": request.user,
      "status": 0,
      "created_at": timezone.now(),
      "applicantText": request.POST.get("applicantText"),
      "applicantDocument": request.POST.get("applicantDocument"),
      "adminComment": None,
    }
    application, created = ModApplication.objects.update_or_create(
      applicant=request.user,
      defaults=data
    )
          
    notification = {
        "title": "Application submit successfully",
        "content": "Your application is being reviewed. Please wait for the approval.",
        "status": "success"
    }  
    messages.success(request, "Your application has been sent. Please wait for the judgement.")
    request.session['mod_app_notification'] = notification
    return redirect("user:info")
    

class importDataView(View):
  def get(self, request):
    # Establish a connection to the SQLite3 database
    database_path = 'db.sqlite3'
    connection = sqlite3.connect(database_path)

    # Get the cursor
    cursor = connection.cursor()

    # Open the CSV file and read its contents
    csv_file_path = 'books4.csv'
    with open(csv_file_path, 'r', encoding='cp437') as file:
      reader = csv.reader(file, delimiter=';')
      next(reader)  # Skip the header row

      count = 0
      # Iterate over each row in the CSV file
      for row in reader:
        count = count + 1
        print(count)
        print(row)
        row = row[0].replace('"','')
        row = row.split(";")
        new_row = []
        for i in range(0, len(row)):
          if i not in [5, 6]:
            new_row.append(row[i])
        print(new_row[0:6])
        # Insert the row data into the books table
        try: 
          cursor.execute('''
              INSERT INTO home_book (codeISBN, title, author, publication, publisher, coverImage, type, liteCate, socieCate, naturCate, techCate, poliCate, romanCate, enterCate, otherCate, language, status)
              VALUES (?, ?, ?, ?, ?, ?, 1, 0, 0, 0, 0, 0, 0, 0, 0, 'English', 1)
          ''', new_row[0:6])
        except:
          print("An exception occured")


    # Commit the changes and close the connection
    connection.commit()
    connection.close()

    # Optional: Refresh Django's database connections
    connections.close_all()
    return HttpResponse("Finished")
  
  
class modManageView(LoginRequiredMixin, View):
  login_url = "user:login"
   
  def get(self, request):
    if request.user.role != 1:
      return redirect("home:index") 
    user_copies = Copy.objects.filter(userID_id=request.user.id)
    borrowancesRequests = Borrowance.objects.filter(copyID__in=user_copies,status=0).order_by('-borrowDate')
    borrowancesHistory = Borrowance.objects.filter(copyID__in=user_copies,status__in=[1,3]).order_by('-borrowDate')
    
    bookApplication = BookApplication.objects.filter(status=0, uploader=request.user)
    bookApplicationHistory = BookApplication.objects.filter(status__in=[1,2], uploader=request.user)
    context = {
      "socialAccount": getSocialAccount(request),
      "borrowancesRequests": borrowancesRequests[:5],
      "borrowancesHistory": borrowancesHistory[:5],
      "bookApplication": bookApplication[:5],
      "bookApplicationHistory": bookApplicationHistory[:5],
    }
    return render(request, "mod/modManageBorrowing.html", context)
  
  def post(self, request,id):
    action = request.POST.get("action")
    borrowance = get_object_or_404(Borrowance.objects.select_related('userID','copyID','copyID__userID','copyID__bookID'), id=id)
    
    if action == "Cancel":
      bookApp = BookApplication.objects.get(id=id, uploader=request.user)
      bookApp.delete()
    
    if action == "Approve":
      borrowance.status = 2
      borrowance.save()
    
      #Send approve email
      mail_subject = 'Biblioteck - Your borrowing request has been approved'
      message = render_to_string('user/template_borrow_result.html', {
        "borrowance": borrowance,
        "action": action,
      })
      to_email = borrowance.userID.email
      
      email = EmailMessage(mail_subject, message, to=[to_email])
      email.send()
    
    if action == "Decline":
      borrowance.status = 1
      borrowance.expiredDate = timezone.now() + timezone.timedelta(days=14)
      borrowance.save()
      
      #Send decline email
      mail_subject = 'Biblioteck - Your borrowing request has been declined'
      message = render_to_string('user/template_borrow_result.html', {
        "borrowance": borrowance,
        "action": action,
        "domain":get_current_site(request),
      })
      to_email = borrowance.userID.email
      
      email = EmailMessage(mail_subject, message, to=[to_email])
      email.send()
    
    return redirect("mod:modManage_get")

    

  
  
class adminManageView(LoginRequiredMixin, View):
  login_url = "user:login"
  
  
  def get(self, request):

    if request.user.role != 2:
      return redirect("home:index")
    
    context = {
      "socialAccount": getSocialAccount(request),
      "applications": ModApplication.objects.filter(status=0)[:5],
      "applicationsHistory": ModApplication.objects.filter(status__in=[1, 2])[:5],
      "bookApplications": BookApplication.objects.filter(status=0)[:5],
      "bookApplicationsHistory": BookApplication.objects.filter(status__in=[1, 2])[:5],
    }
    return render(request, "mod/adminManageBorrowing.html", context)
    
  def post(self, request, id):
    
    action = request.POST.get("action")
    if action == "Approve":
      bookApp = BookApplication.objects.get(id=id)
      bookApp.status = 1
      bookApp.save()

    if action == "Decline":
      bookApp = BookApplication.objects.get(id=id)
      bookApp.status = 2
      bookApp.save()
    
    return redirect("mod:adminManage")
  
  
def deleteBook(request,id):
  book = Book.objects.get(id = id)
  book.delete()
  return redirect("home:shelf", request.user.id)