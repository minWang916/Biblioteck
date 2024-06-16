from allauth.socialaccount import providers
from importlib import import_module
from django.contrib import admin
from django.urls import path, include
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from user.views import signupRedirect

urlpatterns = [
  path('accounts/social/signup/', signupRedirect.as_view(), name="socialaccount_signup"),
]

# Provider urlpatterns, as separate attribute (for reusability).
provider_urlpatterns = []
provider_classes = providers.registry.get_class_list()

# We need to move the OpenID Connect provider to the end. The reason is that
# matches URLs that the builtin providers also match.
#
# NOTE: Only needed if OPENID_CONNECT_URL_PREFIX is blank.
provider_classes = [cls for cls in provider_classes if cls.id != "openid_connect"] + [
    cls for cls in provider_classes if cls.id == "openid_connect"
]

for provider_class in provider_classes:
  prov_mod = import_module(provider_class.get_package() + ".urls")
  prov_urlpatterns = getattr(prov_mod, "urlpatterns", None)
  if prov_urlpatterns:
    provider_urlpatterns += prov_urlpatterns

urlpatterns += provider_urlpatterns