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

# Create your views here.



class indexView(View):
  def get(self, request):
    context = {
      "web":"Home",
      "cssFiles": [],
      "socialAccount": getSocialAccount(request),
      "books": {
        "random": Book.objects.get(id = random.randint(1, 178)),
        "literature": random.sample(list(Book.objects.filter(liteCate = 1)), 6),
        "trending": random.sample(list(Book.objects.all()), 6),
        "favorite": random.sample(list(Book.objects.all()), 6),
      }
    }
    return render(request, 'home/index.html',context)


class faqView(View):
  def get(self, request):
    context = {
      "web":"FAQ",
      "socialAccount": getSocialAccount(request),
    }
    return render(request, 'home/faq.html',context)


class contactView(View):
  def get(self, request):
    context = {
      "web":"Contact",
      "cssFiles": [],
      "socialAccount": getSocialAccount(request),
    }
    return render(request, 'home/contact.html',context)


class galleryView(View):
  def get(self, request):
    books = search(request)
    books = books.annotate(copies_with_status_one=Count('copy', filter=Q(copy__status=1))).filter(copies_with_status_one__gt=0)
    print(len(books))
    
    page = request.GET.get('page', 1)
    paginator = Paginator(books, 10)
    
    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        books = paginator.page(1)
    except EmptyPage:
        books = paginator.page(paginator.num_pages)
        
    min = paginator.num_pages - 4
    max = paginator.num_pages
    
    context = {
      "web":"Search",
      "books": books,
      "cssFiles": ["/static/home/panel.css",
                   "/static/home/search.css"],
      "socialAccount": getSocialAccount(request),
      "min":min,
      "max":max
    }
    return render(request, 'home/gallery.html',context)


class dashboardView(View):
  def get(self, request):
    books = []
    for book in Book.objects.all():
      num_borrow = 0
      num_copy = 0
      for copy in Copy.objects.filter(bookID = book):
        num_borrow += len(Borrowance.objects.filter(copyID = copy))
        num_copy += 1
      books.append({
        "id": book.id,
        "title": book.title,
        "number_borrow": num_borrow,
        "number_copy": num_copy
      })
    sorted_books_borrow = sorted(books, key=lambda x: x['number_borrow'], reverse=True)
    sorted_books_copy = sorted(books, key=lambda x: x['number_copy'], reverse=True)
    users = []
    for user in User.objects.all():
      num_borrow = 0
      num_copy = 0
      num_borrow += len(Borrowance.objects.filter(userID = user))
      num_copy += len(Copy.objects.filter(userID = user))
      users.append({
        "id": user.id,
        "name": user.first_name,
        "number_borrow": num_borrow,
        "number_copy": num_copy
      })
    sorted_users_borrow = sorted(users, key=lambda x: x['number_borrow'], reverse=True)
    sorted_users_copy = sorted(users, key=lambda x: x['number_copy'], reverse=True)
    context = {
      "web":"Dashboard",
      "cssFiles": [],
      "socialAccount": getSocialAccount(request),
      "books": books,
      "books_borrow": sorted_books_borrow[:5],
      "books_copy": sorted_books_copy[:5],
      "users": users,
      "users_borrow": sorted_users_borrow[:5],
      "users_copy": sorted_users_copy[:5],
      "copies": Copy.objects.all(),
      "borrowances": Borrowance.objects.all()
    }
    return render(request, 'home/dashboard.html', context)

class bookView(View):
  def get(self, request, id):
    
    notification_temp = request.session.pop('review_submit', None)
    
    book = Book.objects.get(id=id)
    copies = Copy.objects.filter(bookID=book,status=1)
    mod = User.objects.get(id=copies[0].userID_id)
    providers = Copy.objects.filter(bookID=book, status=1).values('userID__id', 'userID__first_name', 'userID__address').annotate(amount_copies=Count('id'))
    
    form = ReviewForm(initial={"bookID": Book.objects.get(id=id),"userID": request.user,})
    context = {
      "web": book.title,
      "cssFiles": ["/static/home/book.css",
                   ],
      "time": timezone.now(),
      'book': book,
      "providers":providers,
      "form": form,
      "socialAccount": getSocialAccount(request),
      "mod":mod,
      "amount_copies": len(copies),
      "notification":Notification(notification_temp["title"],notification_temp["content"],notification_temp["status"]) if notification_temp else None,
    }
    return render(request, "home/book.html", context)
  
  def post(self, request, id):
    if request.user.is_authenticated == False:
      return redirect("user:login")
    data = {
      "bookID": Book.objects.get(id=id),
      "userID": request.user,
      "rating": request.POST.get("rating"),
      "review": request.POST.get("review"),
      "created_at": timezone.now(),
    }
    
    form = ReviewForm(data)
    book = Book.objects.get(id=id)
    if form.is_valid():

      form.save()
      notification = {
        "title": "Review sent successfully.",
        "content": "Your review has been sent successfully. Thank you for your feedback.",
        "status": "success"
      }  
      messages.success(request, "Profile info updated successfully.")
      request.session['review_submit'] = notification
      return redirect("home:book", id)
    else:
      context = {
      "web": book.title,
      "cssFiles": ["/static/home/book.css",
                   ],
      "time": timezone.now(),
      "book": book,
      "form": form,
      "socialAccount": getSocialAccount(request),
      }
      messages.error(request, "Your rating and review need to follow the format.")
      return render(request, "home/book.html", context)


class bookPDFView(View):
  def get(self, request, id):
    book = Book.objects.get(id=id)
    context = {
      "web": book.title,
      "cssFiles": [],
      "time": timezone.now(),
      'book': book,
      "socialAccount": getSocialAccount(request),
    }
    return render(request, "home/pdfDisplay.html", context)


class shelfView(View):
  template = "home/shelf.html"

  def get(self, request, id):
    owner = User.objects.get(id = id)
    copies = Copy.objects.filter(userID =id).order_by('bookID')
    
    books = search(request)
    books = books.filter(copy__userID_id=id).distinct()
    print(len(books))
    
    page = request.GET.get('page', 1)
    paginator = Paginator(books, 10)
    
    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        books = paginator.page(1)
    except EmptyPage:
        books = paginator.page(paginator.num_pages)
        
    min = paginator.num_pages - 4
    max = paginator.num_pages
    
    
    vendor = User.objects.get(id=id)
    context = {
      "web":vendor.first_name,
      "mod":vendor,
      "socialAccount": getSocialAccount(request),
      "min":min,
      "max":max,
      "books":books,
      "copies": copies,
      "ownerSocialAccount": getSocialAccountByUser(owner),
    }
    return render(request, self.template, context)
  def post(self, request, username):

    return render(request, self.template)


class borrowView(LoginRequiredMixin, View):
  login_url = "user:login"
  def get(self, request, id):
    return redirect("home:book",id)

  def post(self, request, id):
    userID = request.POST.get("userID")
    if userID == "None":
      return redirect("user:login")
    else:
      
      
      mod = User.objects.get(id=request.POST.get("mod_id"))
      book = Book.objects.get(id=id)
      copy = Copy.objects.filter(userID_id=mod.id, bookID_id=book.id).first()

      context = {
          'mod':mod,
          'book':book,
          'copy':copy,
          'web':"Checkout",
          "socialAccount": getSocialAccount(request),
      }
      return render(request, "home/borrowance.html", context)
    
def handling_404(request, exception):
  context = {
    "web":"Page not found",
    "socialAccount": getSocialAccount(request),
  }
  return render(request, '404.html',context)


class resultView(LoginRequiredMixin, View):
  login_url = "user:login"
  
  
  def get(self, request):
    return redirect("home:index")
  def post(self, request):
    
    borrowedDate = timezone.now()
    expiredDate = timezone.now() + timezone.timedelta(days=14)
    status = 0
    deposit = None
    
    copy = Copy.objects.filter(bookID_id=request.POST.get("bookID"),status=1,userID=request.POST.get("modID"))[0]
    copyID_id = copy.id
    userID_id = request.user.id
    
    new_borrowance = Borrowance(
      borrowDate=borrowedDate,
      expiredDate=expiredDate,
      status=status,
      deposit=deposit,
      copyID_id=copyID_id,
      userID_id=userID_id
    )
    new_borrowance.save()
    
    copy.status = 2
    copy.save()
    context={
      "web":"Checkout complete",
      "socialAccount": getSocialAccount(request),
    }
    return render(request, "home/checkoutResult.html",context)