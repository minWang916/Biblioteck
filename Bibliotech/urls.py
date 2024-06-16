from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Pages for everyone (even guests)
    path('', include('home.urls')),

    # User pages
    path('user/', include('user.urls')),

    # For login using all-auth (OAuth2)
    path('accounts/', include('socialplatform.urls')),

    # Moderator pages
    path('mod/', include('moderator.urls')),

    # Admin (Control) pages
    path('control/', include('control.urls')),

    # Default django admin page
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static( settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
    
handler404 = 'home.views.handling_404'