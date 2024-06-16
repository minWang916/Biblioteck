from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include, reverse_lazy
from user.views import *
from django.conf import settings
from django.conf.urls.static import static

app_name = 'user'
urlpatterns = [
    path('register/', registerView.as_view(), name="register"),
    path('login/', loginView.as_view(), name='login'),
    path('logout/', logoutView.as_view(), name='logout'),
    path("password", changePasswordView.as_view(), name="changePassword"),

    path("recover", recoverAccountView.as_view(), name="recover"),
    path("recover/sent", recoverDoneView.as_view(), name="recover_done"),
    path("recover/<uidb64>/<token>", recoverConfirmView.as_view(), name="recover_confirm"),
    path("recover/complete", recoverCompleteView.as_view(), name="recover_complete"),

    path("profile/info/", profileInfoRedirectView.as_view(), name="info"),
    path("profile/userID=<int:id>/", profileInfoView.as_view(), name="wall"),
    path("profile/borrow/", userBorrowanceManagerView.as_view(), name="borrow"),
    path("profile/edit/", profileEditView.as_view(), name="edit"),
    path("activate/<uidb64>/<token>", activate, name="activate"),
]

if settings.DEBUG:
    urlpatterns += static( settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)