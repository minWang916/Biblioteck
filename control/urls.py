from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from control.views import *


app_name = 'control'
urlpatterns = [
    path('', ControlView.as_view(), name="control"),
    path('review/modApplication', ModReviewView.as_view(), name="modReview"),
    path('review/modApplication/<str:action>/<int:userid>', ModDecideView.as_view(), name="modDecide"),
    path('review/newBook', BookReviewView.as_view(), name="bookReview"),
    path('review/newBook/<str:action>/<int:bookid>', BookDecideView.as_view(), name="bookDecide"),
]
