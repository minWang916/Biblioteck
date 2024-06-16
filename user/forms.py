from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError

from home.models import Thought, User


class LoginForm(AuthenticationForm):
  class Meta:
    model = User
    fields = "__all__"


class RegisterForm(UserCreationForm):
  class Meta:
    model = User
    fields = ["username", "email", "password1", "password2",
              "first_name", "last_name", "birthdate", "gender",
              "address", "phoneNum"]
    # fields = "__all__"

  def clean(self):
    email = self.cleaned_data.get('email')
    if User.objects.filter(email=email).exists():
        raise ValidationError("Email exists")
    return self.cleaned_data

class ProfileEditForm(forms.ModelForm):

  class Meta:
    model = User
    fields = ["avatar", "first_name", "last_name", "birthdate", "gender",
              "address", "phoneNum"]
    
class ThoughtForm(forms.ModelForm):
  class Meta:
    model = Thought
    fields = "__all__"