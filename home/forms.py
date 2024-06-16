
from typing import Any, Mapping
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from django.core.exceptions import ValidationError
from django.contrib import messages
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = '__all__'

    def clean(self):
        rating = self.cleaned_data.get('rating')
        review = self.cleaned_data.get('review')
        print(rating)
        print(review)
        if (rating is None and review == ""):
            raise ValidationError("Email exists")
        return self.cleaned_data
    
    
