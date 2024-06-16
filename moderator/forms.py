from django import forms
from home.models import Book, Copy, ModApplication

# create the form here.
class BookForm(forms.ModelForm):
  class Meta:
    model = Book
    fields = '__all__'

class CopyForm(forms.ModelForm):
  class Meta:
    model = Copy
    fields = '__all__'
    widgets = {
      "regDate": forms.HiddenInput(),
      "bookID": forms.HiddenInput(),
      "userID": forms.HiddenInput(),
    }

class ModApplicationForm(forms.ModelForm):
  class Meta:
    model = ModApplication
    fields = "__all__"