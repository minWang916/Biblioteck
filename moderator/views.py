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
from datetime import date, timedelta
import csv
import sqlite3
from django.db import connections

class modView(LoginRequiredMixin, View):
  login_url = "user:login"  # Sets the login URL for redirection if user is not authenticated

  def get(self, request):
      return HttpResponse('Moderator page')  # Returns an HTTP response with 'Moderator page' content for GET requests

  def post(self, request):
      pass  # Placeholder for handling POST requests; currently does nothing



class addBookView(LoginRequiredMixin, View):
  login_url = "user:login"  # Defines the login URL for redirection if user is not authenticated

  def get(self, request):
    if (request.user.is_authenticated and request.user.role > 0):
        form = BookForm(initial={"status": 1})  # Creates a form instance for adding a new book with status set to 1 (default)
        context = {
            "web": "Add Book",  # Sets the page title to "Add Book"
            "cssFiles": [],  # Initializes an empty list for CSS files (none used currently)
            "jsFiles": ["/static/mod/addBook.js"],  # Specifies JavaScript files required for this page
            "form": form,  # Passes the BookForm instance to the context
        }
        return render(request, 'mod/addBook.html', context)  # Renders the 'mod/addBook.html' template with the constructed context
    else:
        messages.error(request, "You don't have the right to add book.")  # Displays an error message if user does not have sufficient rights
        return redirect("home:index")  # Redirects to the home page

  def post(self, request):
    data = request.POST.dict()  # Retrieves POST data as a dictionary
    if (request.user.role > 1):
        data["status"] = 1  # Sets the status of the book to 1 if user role is greater than 1 (indicating higher permissions)
    else:
        data["status"] = 0  # Sets the status of the book to 0 if user role is not greater than 1
    
    form = BookForm(data, request.FILES)  # Creates a BookForm instance with POST data and uploaded files
    
    context = {
        "web": "Add Copy",  # Sets the page title to "Add Copy"
        "cssFiles": [],  # Initializes an empty list for CSS files (none used currently)
        "jsFiles": ["/static/mod/addBook.js"],  # Specifies JavaScript files required for this page
        "form": form,  # Passes the BookForm instance to the context
    }
    
    if form.is_valid():  # Checks if the form data is valid
      newBook = form.save()  # Saves the form data as a new Book object
      if (request.user.role == 2):
          messages.success(request, 'Your book has been added')  # Displays a success message if book is added successfully by a moderator
      else:
          messages.info(request, "Your book will need approval from admin before added.")  # Displays an info message if book requires admin approval
          
          BookApplication.objects.create(  # Creates a BookApplication object for admin approval
              bookID=newBook,
              uploader=request.user,
              status=0,
              created_at=timezone.now(),
          )
          
      return redirect("home:gallery")  # Redirects to the gallery page after book addition
    else:
      notification = Notification("Action failed", "Your form is not valid.", "error")  # Creates a notification object for form validation failure
      context["notification"] = notification  # Adds the notification to the context
      return render(request, 'mod/addBook.html', context)  # Renders the 'mod/addBook.html' template with the constructed context including the notification


class addCopyView(LoginRequiredMixin, View):
  login_url = "user:login"  # Defines the login URL for redirection if user is not authenticated

  def get(self, request, id):
    if not (request.user.is_authenticated and request.user.role >= 1):
        messages.error(request, "You don't have the right to add copy.")  # Displays an error message if user does not have sufficient rights
        return redirect("home:index")  # Redirects to the home page
    
    book = Book.objects.get(id=id)  # Retrieves the Book object based on the provided ID
    form = CopyForm(initial={"bookID": book,  # Creates a CopyForm instance with initial data
                              "userID": request.user,
                              "regDate": date.today()})
    
    copies = Copy.objects.filter(bookID=book.id)  # Retrieves existing copies of the book
    
    context = {
        "web": "Add Copy",  # Sets the page title to "Add Copy"
        "cssFiles": [],  # Initializes an empty list for CSS files (none used currently)
        "book": book,  # Passes the Book object to the context
        "form": form,  # Passes the CopyForm instance to the context
        "copies": copies,  # Passes existing copies of the book to the context
    }
    
    return render(request, 'mod/addCopy.html', context)  # Renders the 'mod/addCopy.html' template with the constructed context

  def post(self, request, id):
    if not (request.user.is_authenticated and request.user.role >= 1):
        messages.error(request, "You don't have the right to add copy.")  # Displays an error message if user does not have sufficient rights
        return redirect("home:index")  # Redirects to the home page
    
    book = Book.objects.get(id=id)  # Retrieves the Book object based on the provided ID
    
    data = {
        "bookID": book,
        "userID": request.user,
        "regDate": date.today(),  # Sets the registration date to the current date
        "note": request.POST.get('note'),  # Retrieves the note from the POST data
        "status": 1  # Sets the status of the copy to 1 (assuming this represents an active status)
    }
    
    form = CopyForm(data)  # Creates a CopyForm instance with the provided data
    
    if form.is_valid():  # Checks if the form data is valid
        form.save()  # Saves the form data as a new Copy object
        messages.success(request, "Your copy has been added successfully.")  # Displays a success message
        return redirect("home:book", id)  # Redirects to the book detail page
        
    else:
        context = {
            "web": "Add Copy",  # Sets the page title to "Add Copy"
            "cssFiles": [],  # Initializes an empty list for CSS files (none used currently)
            "book": book,  # Passes the Book object to the context
            "form": form,  # Passes the CopyForm instance to the context
        }
        messages.error(request, "There is a problem with adding your copy.")  # Displays an error message
        return render(request, 'mod/addCopy.html', context)  # Renders the 'mod/addCopy.html' template with the constructed context including the error message

class editBookView(LoginRequiredMixin, View):
  login_url = "user:login"  # Sets the login URL for redirection if user is not authenticated

  def get(self, request, id):
      if not (request.user.is_authenticated and request.user.role >= 1):
          messages.error(request, "You don't have the right to edit book.")  # Displays an error message if user does not have sufficient rights
          return redirect("home:index")  # Redirects to the home page
      
      book = Book.objects.get(id=id)  # Retrieves the Book object based on the provided ID
      form = BookForm(instance=book)  # Creates a BookForm instance pre-filled with existing book data
      
      context = {
          "web": "Edit Book",  # Sets the page title to "Edit Book"
          "cssFiles": [],  # Initializes an empty list for CSS files (none used currently)
          "book": book,  # Passes the Book object to the context
          "form": form,  # Passes the BookForm instance to the context
      }
      
      return render(request, "mod/editBook.html", context)  # Renders the 'mod/editBook.html' template with the constructed context

  def post(self, request, id):
      print("POST to edit book", id)  # Prints a debug message indicating a POST request to edit a book
      
      if not (request.user.is_authenticated and request.user.role >= 1):
          messages.error(request, "You don't have the right to edit book.")  # Displays an error message if user does not have sufficient rights
          return redirect("home:index")  # Redirects to the home page
      
      book = Book.objects.get(id=id)  # Retrieves the Book object based on the provided ID
      data = request.POST.dict()  # Retrieves POST data as a dictionary
      data["status"] = book.status  # Retrieves existing status of the book
      
      form = BookForm(data, request.FILES, instance=book)  # Creates a BookForm instance with updated data
      
      if form.is_valid():  # Checks if the form data is valid
          print("valid")  # Prints debug message indicating valid form data
          form.save()  # Saves the form data to update the book object
          messages.success(request, "The book has been edited successfully.")  # Displays a success message
          return redirect("mod:addCopy", id)  # Redirects to the 'addCopy' view for the same book
      
      else:
          print("invalid")  # Prints debug message indicating invalid form data
          
          context = {
              "web": "Edit Book",  # Sets the page title to "Edit Book"
              "cssFiles": [],  # Initializes an empty list for CSS files (none used currently)
              "book": book,  # Passes the Book object to the context
              "form": form,  # Passes the invalid BookForm instance to the context
          }
          
          return render(request, "mod/editBook.html", context)  # Renders the 'mod/editBook.html' template with the constructed context including the error messages


class editCopyView(LoginRequiredMixin, View):
  login_url = "user:login"  # Sets the login URL for redirection if user is not authenticated

  def get(self, request, id):
      copy = Copy.objects.get(id=id)  # Retrieves the Copy object based on the provided ID
      
      # Checks if the user is authenticated, has sufficient role permissions, and is the owner of the copy
      if not (request.user.is_authenticated and request.user.role >= 1 and request.user == copy.userID):
          messages.error(request, "You don't have the right to edit copy.")  # Displays an error message if conditions are not met
          return redirect("home:index")  # Redirects to the home page
      
      form = CopyForm(instance=copy)  # Creates a CopyForm instance pre-filled with existing copy data
      
      context = {
          "web": "Edit Book",  # Sets the page title to "Edit Book"
          "cssFiles": [],  # Initializes an empty list for CSS files (none used currently)
          "copy": copy,  # Passes the Copy object to the context
          "form": form,  # Passes the CopyForm instance to the context
      }
      
      return render(request, "mod/editCopy.html", context)  # Renders the 'mod/editCopy.html' template with the constructed context

  def post(self, request, id):
      if not (request.user.is_authenticated and request.user.role >= 1):
          messages.error(request, "You don't have the right to edit book.")  # Displays an error message if user does not have sufficient rights
          return redirect("home:index")  # Redirects to the home page
      
      copy = Copy.objects.get(id=id)  # Retrieves the Copy object based on the provided ID
      print(request.POST.get("note"))  # Prints the 'note' data received in the POST request
      
      data = {
          "userID": copy.userID,
          "bookID": copy.bookID,
          "status": request.POST.get("status"),  # Retrieves the 'status' from POST data
          "note": request.POST.get("note"),  # Retrieves the 'note' from POST data
          "regDate": copy.regDate,
      }
      
      form = CopyForm(data, instance=copy)  # Creates a CopyForm instance with updated data
      
      context = {
          "web": "Edit Book",  # Sets the page title to "Edit Book"
          "cssFiles": [],  # Initializes an empty list for CSS files (none used currently)
          "copy": copy,  # Passes the Copy object to the context
          "form": form,  # Passes the CopyForm instance to the context
      }
      
      if form.is_valid():  # Checks if the form data is valid
          form.save()  # Saves the form data to update the copy object
          messages.success(request, "The copy has been edited successfully.")  # Displays a success message
          return redirect("mod:editCopy", id)  # Redirects to the 'editCopy' view for the same copy
      
      else:
          return render(request, "mod/editCopy.html", context)  # Renders the 'mod/editCopy.html' template with the constructed context including the error messages



class applyModView(LoginRequiredMixin, View):
  login_url = "user:login"  # Sets the login URL for redirection if user is not authenticated

  def get(self, request):
      if request.user.role > 0:
          messages.warning(request, "You are already a moderator.")  # Displays a warning if the user is already a moderator
          return redirect("home:index")  # Redirects to the home page
      
      form = ModApplicationForm(
          initial={
              "applicant": request.user,
              "status": 0,
              "created_at": timezone.now(),
          }
      )
      
      context = {
          "web": "Mod Apply",  # Sets the page title to "Mod Apply"
          "form": form,  # Passes the ModApplicationForm instance to the context
          "socialAccount": getSocialAccount(request),  # Retrieves social account details based on the request
      }
      
      return render(request, "mod/modApply.html", context)  # Renders the 'mod/modApply.html' template with the constructed context

  def post(self, request):
      if request.user.role > 0:
          messages.warning(request, "You are already a moderator.")  # Displays a warning if the user is already a moderator
          return redirect("home:index")  # Redirects to the home page
      
      # Updates the user profile with additional application information
      userprofile = User.objects.get(id=request.user.id)
      userprofile.phoneNum = request.POST.get("phone")
      userprofile.address = request.POST.get("address")
      userprofile.availableWorkingHours = request.POST.get("working_hours")
      userprofile.description = request.POST.get("description")
      userprofile.save()  # Saves the updated user profile
      
      # Constructs the data dictionary for ModApplication creation or update
      data = {
          "applicant": request.user,
          "status": 0,
          "created_at": timezone.now(),
          "applicantText": request.POST.get("applicantText"),  # Retrieves applicant text from POST data
          "applicantDocument": request.POST.get("applicantDocument"),  # Retrieves applicant document from POST data
          "adminComment": None,  # Initializes admin comment as None
      }
      
      # Updates or creates a ModApplication instance based on the applicant
      application, created = ModApplication.objects.update_or_create(
          applicant=request.user,
          defaults=data
      )
      
      # Prepares a success notification to be displayed
      notification = {
          "title": "Application submit successfully",
          "content": "Your application is being reviewed. Please wait for the approval.",
          "status": "success"
      }
      
      messages.success(request, "Your application has been sent. Please wait for the judgment.")  # Displays a success message
      request.session['mod_app_notification'] = notification  # Stores the notification in session for display on another page
      
      return redirect("user:info")  # Redirects to the user info page after successful application submission

    

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
  login_url = "user:login"  # Sets the login URL for redirection if user is not authenticated

  def get(self, request):
      if request.user.role != 1:  # Checks if the user role is not 1 (not a moderator)
          return redirect("home:index")  # Redirects to the home page
      
      # Retrieves copies owned by the current user (moderator)
      user_copies = Copy.objects.filter(userID_id=request.user.id)
      
      # Retrieves borrowing requests for the user's copies that are pending (status=0) and orders by borrow date descending
      borrowancesRequests = Borrowance.objects.filter(copyID__in=user_copies, status=0).order_by('-borrowDate')
      
      # Retrieves borrowing history for the user's copies that are borrowed or returned (status=1 or 3) and orders by borrow date descending
      borrowancesHistory = Borrowance.objects.filter(copyID__in=user_copies, status__in=[1, 3]).order_by('-borrowDate')
      
      # Retrieves book applications submitted by the current user (moderator) that are pending (status=0)
      bookApplication = BookApplication.objects.filter(status=0, uploader=request.user)
      
      # Retrieves book application history for the current user (moderator) that are approved or declined (status=1 or 2)
      bookApplicationHistory = BookApplication.objects.filter(status__in=[1, 2], uploader=request.user)
      
      context = {
          "socialAccount": getSocialAccount(request),  # Retrieves social account details based on the request
          "borrowancesRequests": borrowancesRequests[:5],  # Passes the first 5 borrowing requests to the context
          "borrowancesHistory": borrowancesHistory[:5],  # Passes the first 5 borrowing history entries to the context
          "bookApplication": bookApplication[:5],  # Passes the first 5 book applications to the context
          "bookApplicationHistory": bookApplicationHistory[:5],  # Passes the first 5 book application history entries to the context
      }
      
      return render(request, "mod/modManageBorrowing.html", context)  # Renders the 'mod/modManageBorrowing.html' template with the constructed context
    
  def post(self, request, id):
      action = request.POST.get("action")  # Retrieves the action (Approve/Decline/Cancel) from POST data
      
      # Retrieves the Borrowance object based on the ID from the POST data, or returns a 404 page if not found
      borrowance = get_object_or_404(Borrowance.objects.select_related('userID', 'copyID', 'copyID__userID', 'copyID__bookID'), id=id)
      
      if action == "Cancel":
          # Deletes the BookApplication object if the action is "Cancel"
          bookApp = BookApplication.objects.get(id=id, uploader=request.user)
          bookApp.delete()
      
      if action == "Approve":
          # Updates Borrowance status to 2 (approved) and sets expiredDate to 14 days from current time
          borrowance.status = 2
          borrowance.expiredDate = timezone.now() + timezone.timedelta(days=14)
          borrowance.save()
          
          # Sends an approval email to the borrower
          mail_subject = 'Biblioteck - Your borrowing request has been approved'
          message = render_to_string('user/template_borrow_result.html', {
              "borrowance": borrowance,
              "action": action,
          })
          to_email = borrowance.userID.email
          email = EmailMessage(mail_subject, message, to=[to_email])
          email.send()
      
      if action == "Decline":
          # Updates Borrowance status to 1 (declined)
          borrowance.status = 1
          borrowance.save()
          
          # Sends a decline email to the borrower
          mail_subject = 'Biblioteck - Your borrowing request has been declined'
          message = render_to_string('user/template_borrow_result.html', {
              "borrowance": borrowance,
              "action": action,
              "domain": get_current_site(request),
          })
          to_email = borrowance.userID.email
          email = EmailMessage(mail_subject, message, to=[to_email])
          email.send()
      
      return redirect("mod:modManage_get")  # Redirects to the GET method of modManageView after processing the POST request

class adminManageView(LoginRequiredMixin, View):
  login_url = "user:login"  # Sets the login URL for redirection if user is not authenticated
    
  def get(self, request):
      if request.user.role != 2:  # Checks if the user role is not 2 (admin)
          return redirect("home:index")  # Redirects to the home page if not admin
      
      # Constructs context with necessary data for rendering the template
      context = {
          "socialAccount": getSocialAccount(request),  # Retrieves social account details based on the request
          "applications": ModApplication.objects.filter(status=0)[:5],  # Retrieves pending moderator applications (status=0) and limits to 5 entries
          "applicationsHistory": ModApplication.objects.filter(status__in=[1, 2])[:5],  # Retrieves approved or declined moderator applications (status=1 or 2) and limits to 5 entries
          "bookApplications": BookApplication.objects.filter(status=0)[:5],  # Retrieves pending book applications (status=0) and limits to 5 entries
          "bookApplicationsHistory": BookApplication.objects.filter(status__in=[1, 2])[:5],  # Retrieves approved or declined book applications (status=1 or 2) and limits to 5 entries
      }
      
      return render(request, "mod/adminManageBorrowing.html", context)  # Renders the 'mod/adminManageBorrowing.html' template with the constructed context
    
  def post(self, request, id):
      action = request.POST.get("action")  # Retrieves the action (Approve/Decline) from POST data
      
      if action == "Approve":
          # Retrieves the BookApplication object based on ID from POST data or returns a 404 page if not found
          bookApp = get_object_or_404(BookApplication.objects, id=id)
          bookApp.status = 1  # Updates the status of the book application to 1 (approved)
          bookApp.save()
      
      if action == "Decline":
          # Retrieves the BookApplication object based on ID from POST data or returns a 404 page if not found
          bookApp = get_object_or_404(BookApplication.objects, id=id)
          bookApp.status = 2  # Updates the status of the book application to 2 (declined)
          bookApp.save()
      
      return redirect("mod:adminManage")  # Redirects to the GET method of adminManageView after processing the POST request
  
  
def deleteBook(request,id):
    book = Book.objects.get(id = id)
    book.delete()
    return redirect("home:shelf", request.user.id)