from django.db import models
from django.contrib.auth.models import AbstractUser
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# Create your models here.
def getBookImageURL(instance, filename):
  if instance.id != None:
      return "book/{}/coverImage.png".format(instance.id)
  else:
    queryset = Book.objects.all().order_by('pk')
    last = queryset.last()
    last_id = last.id
    file_number = last_id+1
    return "book/{}/coverImage.png".format(file_number)

def getBookPDFURL(instance, filename):
  if instance.id != None:
      return "book/{}/pdfFile.pdf".format(instance.id)
  else:
    queryset = Book.objects.all().order_by('pk')
    last = queryset.last()
    last_id = last.id
    file_number = last_id+1
    return "book/{}/pdfFile.pdf".format(file_number)

def getUserImageURL(instance, filename):
  if instance.id != None:
      return "user/{}/avatar.png".format(instance.id)
  else:
    queryset = User.objects.all().order_by('pk')
    last = queryset.last()
    last_id = last.id
    file_number = last_id+1
    return "user/{}/avatar.png".format(file_number)

class User(AbstractUser):
  email = models.EmailField(null=False, blank=False, unique=True, help_text="Required", error_messages="This field is compulsory and must follow email format")
  avatar = models.ImageField(upload_to=getUserImageURL, null=True, blank=True)
  birthdate = models.DateField(null=True, blank=True)
  genderChoices = (
    (0, "male"),
    (1, "female"),
    (2, "other")
  )
  gender = models.IntegerField(choices=genderChoices, null=False, default=2)
  address = models.CharField(max_length=200, null=True, blank=True)
  phoneNum = models.CharField(max_length=50, null=True, blank=True)
  roleChoices = (
    (0, "user"),
    (1, "moderator"),
    (2, "admin"),
    (3, "banned")
  )
  role = models.IntegerField(choices=roleChoices, default=0)
  description = models.CharField(max_length=1500, null=True, blank=True)
  availableWorkingHours = models.CharField(max_length=300, null=True, blank=True)

class Book(models.Model):
  title = models.CharField(max_length=200, null=False, default="UNTITLED")
  author = models.CharField(max_length=200, null=False, default="UNKNOWN")
  typeChoices = (
    (0, "article"),
    (1, "book"),
    (2, "magazine"),
    (3, "video/audio"),
    (4, "comic"),
    (5, "other")
  )
  type = models.IntegerField(choices=typeChoices, null=True, default=0)
  liteCate = models.BooleanField(default=False, blank=True, null=True)
  socieCate = models.BooleanField(default=False, blank=True, null=True)
  naturCate = models.BooleanField(default=False, blank=True, null=True)
  techCate = models.BooleanField(default=False, blank=True, null=True)
  poliCate = models.BooleanField(default=False, blank=True, null=True)
  romanCate = models.BooleanField(default=False, blank=True, null=True)
  enterCate = models.BooleanField(default=False, blank=True, null=True)
  otherCate = models.BooleanField(default=False, blank=True, null=True)
  language = models.CharField(max_length=200, null=True, blank=True)
  description = models.TextField(max_length=1500, null=True, blank=True)
  coverImage = models.ImageField(upload_to=getBookImageURL, null=True, blank=True)
  pdfFile = models.FileField(upload_to=getBookPDFURL,null=True,blank=True)
  publisher = models.CharField(max_length=200, null=True, blank=True)
  publication = models.CharField(max_length=50, null=True, blank=True)
  codeISBN = models.CharField(max_length=50, null=True, blank=True)
  statusChoices = (
    (0, "pending"),
    (1, "accepted"),
    (2, "rejected")
  )
  status = models.IntegerField(choices=statusChoices, default=0, null=True)
  id = models.AutoField(primary_key=True)
  manual = models.BooleanField(default=True, null = True, blank = True)

  def __str__(self) :
    return str(self.id) + ". " + self.title


class Copy(models.Model):
  bookID = models.ForeignKey(Book, null=False, on_delete=models.CASCADE)
  userID = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
  statusChoices = (
    (0, "hidden"),
    (1, "available"),
    (2, "borrowed"),
    (3, "unavailable")
  )
  status = models.IntegerField(choices=statusChoices, default=0)
  note = models.TextField(max_length=200, null=True, blank=True)
  regDate = models.DateTimeField(null=False)

  def __str__(self) :
    return str(self.id) + ". " + self.bookID.title


class Borrowance(models.Model):
  copyID = models.ForeignKey(Copy, on_delete=models.CASCADE)
  userID = models.ForeignKey(User, on_delete=models.CASCADE)
  borrowDate = models.DateTimeField(null=False)
  expiredDate = models.DateTimeField(null=False)
  statusChoices = (
    (0, "request"),
    (1, "double-check"),
    (2, "borrowing"),
    (3, "returned"),
    (4, "overdue"),
    (5, "lost")
  )
  status = models.IntegerField(choices=statusChoices, default=0, null=False)
  deposit = models.FloatField(default=0, null=True, blank=True)


class Review(models.Model):
  bookID = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
  userID = models.ForeignKey(User, on_delete=models.CASCADE)

  def validateRating(value):
    if (value > 5 or value < 1):
      raise ValidationError(
        _('%(value)s is not valid'),
        params={'value': value},
      )
    
  rating = models.IntegerField(validators=[validateRating], null=True, blank=True)
  review = models.TextField(max_length=1500, null=True, blank=True)
  created_at = models.DateTimeField(default=timezone.now)

  def __str__(self) :
    return "Review " + str(self.id)
  
def getApplicantDocURL(instance, filename):
  return "user/{}/modApplication.pdf".format(instance.applicant.id)

class ModApplication(models.Model):
  applicant = models.ForeignKey(User, on_delete=models.CASCADE)
  applicantDocument = models.FileField(upload_to=getApplicantDocURL,null=True,blank=True)
  applicantText = models.TextField(max_length=1500, null=True, blank=True)
  adminComment = models.TextField(max_length=1500, null=True, blank=True)
  statusChoices = (
    (0, "applying"),
    (1, "approved"),
    (2, "denied"),
  )
  status = models.IntegerField(choices=statusChoices, default=0, null=False)
  created_at = models.DateTimeField(default=timezone.now)
  
class Thought(models.Model):
  userID = models.ForeignKey(User, on_delete=models.CASCADE)
  thought = models.TextField(max_length=1500, null=False)
  created_at = models.DateTimeField(default=timezone.now)
  
class BookApplication(models.Model):
  bookID = models.ForeignKey(Book, on_delete=models.CASCADE)
  uploader = models.ForeignKey(User, on_delete=models.CASCADE)
  statusChoices = (
    (0, "applying"),
    (1, "approved"),
    (2, "denied"),
  )
  status = models.IntegerField(choices=statusChoices, default=0, null=False)
  created_at = models.DateTimeField(default=timezone.now)