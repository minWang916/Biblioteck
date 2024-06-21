from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import HttpResponseRedirect, FileResponse
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render
from django.views import View
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from home.forms import *
from home.models import *
from home.functions import *
import os, random, time, operator
from home.util import Notification

class indexView(View):
  def get(self, request):
    # Constructs the context dictionary for rendering the index page
    context = {
        "web": "Home",  # Sets the page title to "Home"
        "cssFiles": [],  # Initializes an empty list for CSS file paths
        "socialAccount": getSocialAccount(request),  # Retrieves social account details based on the request
        "books": {
            "random": Book.objects.get(id=random.randint(1, 178)),  # Retrieves a random Book object within the ID range 1 to 178
            "literature": random.sample(list(Book.objects.filter(liteCate=1)), 6),  # Retrieves 6 random Book objects filtered by liteCate = 1
            "trending": random.sample(list(Book.objects.all()), 6),  # Retrieves 6 random Book objects from all available books
            "favorite": random.sample(list(Book.objects.all()), 6),  # Retrieves 6 random Book objects from all available books
        }
    }
    return render(request, 'home/index.html', context)  # Renders the 'home/index.html' template with the constructed context


class faqView(View):
  def get(self, request):
    # Constructs the context dictionary for rendering the FAQ page
    context = {
        "web": "FAQ",  # Sets the page title to "FAQ"
        "socialAccount": getSocialAccount(request),  # Retrieves social account details based on the request
    }
    return render(request, 'home/faq.html', context)  # Renders the 'home/faq.html' template with the constructed context


class contactView(View):
  def get(self, request):
    # Constructs the context dictionary for rendering the Contact page
    context = {
        "web": "Contact",  # Sets the page title to "Contact"
        "cssFiles": [],  # Initializes an empty list for CSS files (currently none)
        "socialAccount": getSocialAccount(request),  # Retrieves social account details based on the request
    }
    return render(request, 'home/contact.html', context)  # Renders the 'home/contact.html' template with the constructed context


class galleryView(View):
  def get(self, request):
    # Performs a search based on the request and filters books with at least one copy status of 1
    books = search(request)
    books = books.annotate(copies_with_status_one=Count('copy', filter=Q(copy__status=1))).filter(copies_with_status_one__gt=0)
    print(len(books))  # Prints the number of books found after filtering
    
    page = request.GET.get('page', 1)
    paginator = Paginator(books, 10)  # Paginates the filtered books, displaying 10 books per page
    
    try:
        books = paginator.page(page)  # Retrieves the requested page of books
    except PageNotAnInteger:
        books = paginator.page(1)  # If page is not an integer, defaults to the first page
    except EmptyPage:
        books = paginator.page(paginator.num_pages)  # If page is out of range, returns the last page of results
    
    min = paginator.num_pages - 4  # Calculates the minimum page number to display in pagination
    max = paginator.num_pages  # Sets the maximum page number to display in pagination
    
    context = {
        "web": "Search",  # Sets the page title to "Search"
        "books": books,  # Passes paginated books to the context for rendering
        "cssFiles": ["/static/home/panel.css", "/static/home/search.css"],  # Defines CSS files needed for styling
        "socialAccount": getSocialAccount(request),  # Retrieves social account details based on the request
        "min": min,  # Minimum page number for pagination
        "max": max  # Maximum page number for pagination
    }
    return render(request, 'home/gallery.html', context)  # Renders the 'home/gallery.html' template with the constructed context


class dashboardView(View):
  def get(self, request):
    # Initialize an empty list to store book statistics
    books = []
    
    # Iterate through all books in the database
    for book in Book.objects.all():
        num_borrow = 0  # Initialize the count of borrowances for the current book
        num_copy = 0    # Initialize the count of copies for the current book
        
        # Iterate through copies of the current book
        for copy in Copy.objects.filter(bookID=book):
            # Count the number of borrowances for each copy of the book
            num_borrow += len(Borrowance.objects.filter(copyID=copy))
            num_copy += 1  # Increment the copy count
        
        # Append book statistics to the list
        books.append({
            "id": book.id,
            "title": book.title,
            "number_borrow": num_borrow,
            "number_copy": num_copy
        })
    
    # Sort books based on the number of borrowances and copies
    sorted_books_borrow = sorted(books, key=lambda x: x['number_borrow'], reverse=True)
    sorted_books_copy = sorted(books, key=lambda x: x['number_copy'], reverse=True)
    
    # Initialize an empty list to store user statistics
    users = []
    
    # Iterate through all users in the database
    for user in User.objects.all():
        num_borrow = len(Borrowance.objects.filter(userID=user))  # Count borrowances for the user
        num_copy = len(Copy.objects.filter(userID=user))          # Count copies managed by the user
        
        # Append user statistics to the list
        users.append({
            "id": user.id,
            "name": user.first_name,
            "number_borrow": num_borrow,
            "number_copy": num_copy
        })
    
    # Sort users based on the number of borrowances and copies
    sorted_users_borrow = sorted(users, key=lambda x: x['number_borrow'], reverse=True)
    sorted_users_copy = sorted(users, key=lambda x: x['number_copy'], reverse=True)
    
    # Construct the context dictionary for rendering the dashboard
    context = {
        "web": "Dashboard",                             # Title of the page
        "cssFiles": [],                                 # Empty list for CSS files
        "socialAccount": getSocialAccount(request),     # Retrieve social account details
        "books": books,                                 # List of all books with statistics
        "books_borrow": sorted_books_borrow[:5],        # Top 5 books by borrow count
        "books_copy": sorted_books_copy[:5],            # Top 5 books by copy count
        "users": users,                                 # List of all users with statistics
        "users_borrow": sorted_users_borrow[:5],        # Top 5 users by borrow count
        "users_copy": sorted_users_copy[:5],            # Top 5 users by copy count
        "copies": Copy.objects.all(),                   # All copies in the database
        "borrowances": Borrowance.objects.all()         # All borrowances in the database
    }
    
    return render(request, 'home/dashboard.html', context)  # Render the dashboard template with the constructed context


class bookView(View):
  def get(self, request, id):
    notification_temp = request.session.pop('review_submit', None)  # Retrieve and remove review submission notification
    
    book = Book.objects.get(id=id)  # Get the book object with the given ID
    copies = Copy.objects.filter(bookID=book, status=1)  # Get active copies of the book
    mod = User.objects.get(id=copies[0].userID_id)  # Get the moderator of the first copy
    
    # Retrieve providers (users) who have copies of the book
    providers = Copy.objects.filter(bookID=book, status=1).values('userID__id', 'userID__first_name', 'userID__address').annotate(amount_copies=Count('id'))
    
    form = ReviewForm(initial={"bookID": Book.objects.get(id=id), "userID": request.user})  # Initialize review form
    
    # Construct the context dictionary for rendering the book view
    context = {
        "web": book.title,                           # Title of the book page
        "cssFiles": ["/static/home/book.css"],       # List of CSS files
        "time": timezone.now(),                      # Current time
        'book': book,                                # Book object
        "providers": providers,                      # Providers of the book
        "form": form,                                # Review form
        "socialAccount": getSocialAccount(request),  # Retrieve social account details
        "mod": mod,                                  # Moderator of the book
        "amount_copies": len(copies),                # Number of active copies
        "notification": Notification(notification_temp["title"], notification_temp["content"], notification_temp["status"]) if notification_temp else None,  # Notification if exists
    }
    
    return render(request, "home/book.html", context)  # Render the book template with the constructed context

  def post(self, request, id):
    if not request.user.is_authenticated:  # Redirect if user is not authenticated
        return redirect("user:login")
    
    data = {  # Construct data dictionary for review submission
        "bookID": Book.objects.get(id=id),          # Book ID
        "userID": request.user,                     # User ID
        "rating": request.POST.get("rating"),       # Rating from form
        "review": request.POST.get("review"),       # Review text from form
        "created_at": timezone.now(),               # Current time
    }
    
    form = ReviewForm(data)  # Initialize review form with data
    
    book = Book.objects.get(id=id)  # Get the book object
    
    if form.is_valid():
        form.save()  # Save the valid form data
        
        # Notification details for successful review submission
        notification = {
            "title": "Review sent successfully.",
            "content": "Your review has been sent successfully. Thank you for your feedback.",
            "status": "success"
        }  
        
        messages.success(request, "Profile info updated successfully.")  # Success message
        request.session['review_submit'] = notification  # Store notification in session
        
        return redirect("home:book", id)  # Redirect to the book page
    else:
        context = {
            "web": book.title,                          # Title of the book page
            "cssFiles": ["/static/home/book.css"],      # List of CSS files
            "time": timezone.now(),                     # Current time
            "book": book,                               # Book object
            "form": form,                               # Review form
            "socialAccount": getSocialAccount(request), # Retrieve social account details
        }
        
        messages.error(request, "Your rating and review need to follow the format.")  # Error message
        
        return render(request, "home/book.html", context)  # Render the book template with the constructed context



class bookPDFView(View):
  def get(self, request, id):
    book = Book.objects.get(id=id)  # Get the book object with the given ID
    
    # Construct the context dictionary for rendering the PDF display page
    context = {
        "web": book.title,                           # Title of the book page
        "cssFiles": [],                              # Empty list for CSS files
        "time": timezone.now(),                      # Current time
        'book': book,                                # Book object
        "socialAccount": getSocialAccount(request),  # Retrieve social account details
    }
    
    return render(request, "home/pdfDisplay.html", context)  # Render the PDF display template with the constructed context



class shelfView(View):
    template = "home/shelf.html"

    def get(self, request, id):
        # Retrieve the owner based on the given id
        owner = User.objects.get(id=id)
        
        # Retrieve copies owned by the user and order them by bookID
        copies = Copy.objects.filter(userID=id).order_by('bookID')
        
        # Perform search based on request and filter books by user ID
        books = search(request)
        books = books.filter(copy__userID_id=id).distinct()
        print(len(books))  # Print the number of books found (for debugging)
        
        # Paginate the books with 10 items per page
        page = request.GET.get('page', 1)
        paginator = Paginator(books, 10)
        
        try:
            books = paginator.page(page)
        except PageNotAnInteger:
            books = paginator.page(1)
        except EmptyPage:
            books = paginator.page(paginator.num_pages)
        
        # Calculate pagination limits for navigation
        min = paginator.num_pages - 4
        max = paginator.num_pages
        
        # Retrieve the vendor (user) based on the given id
        vendor = User.objects.get(id=id)
        
        # Construct the context dictionary for rendering the shelf.html template
        context = {
            "web": vendor.first_name,  # Sets the page title to the vendor's first name
            "mod": vendor,  # Passes the vendor user object
            "socialAccount": getSocialAccount(request),  # Retrieves social account details based on the request
            "min": min,  # Passes the minimum pagination page
            "max": max,  # Passes the maximum pagination page
            "books": books,  # Passes the paginated books
            "copies": copies,  # Passes the copies owned by the user
            "ownerSocialAccount": getSocialAccountByUser(owner),  # Retrieves social account details for the owner
        }
        return render(request, self.template, context)

    def post(self, request):
        # Handles POST requests (currently renders the shelf.html template)
        return render(request, self.template)


class borrowView(LoginRequiredMixin, View):
    login_url = "user:login"

    def get(self, request, id):
        # Redirects to the book view page with the specified book ID
        return redirect("home:book", id=id)

    def post(self, request, id):
        userID = request.POST.get("userID")
        
        # Redirects to the login page if userID is "None"
        if userID == "None":
            return redirect("user:login")
        else:
            mod = User.objects.get(id=request.POST.get("mod_id"))
            book = Book.objects.get(id=id)
            
            # Retrieves the copy based on the mod_id and book_id
            copy = Copy.objects.filter(userID_id=mod.id, bookID_id=book.id).first()

            # Constructs the context for rendering the borrowance.html template
            context = {
                'mod': mod,  # Passes the moderator user object
                'book': book,  # Passes the book object
                'copy': copy,  # Passes the copy object
                'web': "Checkout",  # Sets the page title to "Checkout"
                "socialAccount": getSocialAccount(request),  # Retrieves social account details based on the request
            }
            return render(request, "home/borrowance.html", context)


def handling_404(request, exception):
    # Handles 404 errors by rendering a custom 404.html page
    context = {
        "web": "Page not found",  # Sets the page title to "Page not found"
        "socialAccount": getSocialAccount(request),  # Retrieves social account details based on the request
    }
    return render(request, '404.html', context)


class resultView(LoginRequiredMixin, View):
  login_url = "user:login"  # Sets the login URL for redirection if user is not authenticated

  def get(self, request):
    return redirect("home:index")  # Redirects to the index page for GET requests

  def post(self, request):
    # Sets the borrowedDate to the current time in UTC
    borrowedDate = timezone.now()
    
    # Sets the expiredDate to 14 days from the current time in UTC
    expiredDate = timezone.now() + timezone.timedelta(days=14)
    
    # Sets the initial status of the borrowance
    status = 0
    
    # Sets the deposit to None initially
    deposit = None
    
    # Retrieves the copy object based on the provided bookID, status, and modID
    copy = Copy.objects.filter(
        bookID_id=request.POST.get("bookID"),
        status=1,
        userID=request.POST.get("modID")
    ).first()
    
    # Retrieves the ID of the copy
    copyID_id = copy.id
    
    # Retrieves the ID of the current user
    userID_id = request.user.id
    
    # Creates a new Borrowance object with the retrieved data and saves it to the database
    new_borrowance = Borrowance(
        borrowDate=borrowedDate,
        expiredDate=expiredDate,
        status=status,
        deposit=deposit,
        copyID_id=copyID_id,
        userID_id=userID_id
    )
    new_borrowance.save()
    
    # Updates the status of the copy to 2 (indicating it's borrowed)
    copy.status = 2
    copy.save()
    
    # Constructs the context for rendering the checkoutResult.html template
    context = {
        "web": "Checkout complete",  # Sets the page title to "Checkout complete"
        "socialAccount": getSocialAccount(request),  # Retrieves social account details based on the request
    }
    
    # Renders the checkoutResult.html template with the constructed context
    return render(request, "home/checkoutResult.html", context)
