from allauth.socialaccount.models import SocialAccount
from home.models import *
from word_forms.word_forms import get_word_forms
from autocorrect import Speller
from django.db.models import Q


def getSocialAccount(request):
  if (request.user.is_authenticated):
    try:
      socialAccount = SocialAccount.objects.get(user = request.user)
    except SocialAccount.DoesNotExist:
      socialAccount = None
  else:
    socialAccount = None
  return socialAccount

def getSocialAccountByUser(user):
  try:
    socialAccount = SocialAccount.objects.get(user = user)
  except SocialAccount.DoesNotExist:
    socialAccount = None
  return socialAccount


def search(request):
  booksByKeyword = Book.objects.none()
  if request.GET.get("book_search"):
    keyword = request.GET.get("book_search").strip()
    spell = Speller(lang='en')
    spell_corrected_keyword = spell(keyword)
    wordForms = get_word_forms(spell_corrected_keyword)
    wordFormsList = [keyword,spell_corrected_keyword]
    if len(wordForms['n']) != 0:
        wordFormsList.extend(wordForms['n'])
    if len(wordForms['a']) != 0:
        wordFormsList.extend(wordForms['a'])
    if len(wordForms['v']) != 0:
        wordFormsList.extend(wordForms['v'])
    if len(wordForms['r']) != 0:
        wordFormsList.extend(wordForms['r'])
    
    for keyword in wordFormsList:
      booksByTitle = Book.objects.filter(title__icontains=keyword)
      booksByAuthor = Book.objects.filter(author__icontains=keyword)
      booksByKeyword |= booksByTitle | booksByAuthor

  else:
    booksByKeyword = Book.objects.all()
      
  booksByCategories = Book.objects.none()  

  if request.GET.getlist("category"):
    selected_categories = request.GET.getlist('category')
    filter_condition = Q()
    for category in selected_categories:
      filter_condition &= Q(**{category: True})
    booksByCategories = Book.objects.filter(filter_condition)
  else:
    booksByCategories = Book.objects.all()  
  
  books = booksByKeyword & booksByCategories
  return books