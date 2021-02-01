"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import rest_framework.exceptions
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path
from django.views.generic.base import TemplateView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from app.settings import DEBUG
from app.views import Http404

handler404 = Http404
handler500 = rest_framework.exceptions.server_error
handler400 = rest_framework.exceptions.bad_request

schema_view = get_schema_view(
    openapi.Info(
        title="Mulgyeol API Docs",
        default_version="v1",
        description="Automate tasks by using a simple and powerful API.",
        # terms_of_service="https://www.google.com/policies/terms/",
        # contact=openapi.Contact(email="contact@snippets.local"),
        # license=openapi.License(name="BSD License"),
    ),
    validators=["flex", "ssv"],
    public=DEBUG,
    permission_classes=(permissions.AllowAny,),
)


docs_view = schema_view.with_ui("redoc", cache_timeout=0)
swagger_view = schema_view.with_ui("swagger", cache_timeout=0)

if not DEBUG:
    docs_view = login_required(docs_view)
    swagger_view = login_required(swagger_view)


urlpatterns = [
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    path("highlighter/", include("highlighter_api.urls")),
    path("", include("mgauth.urls")),
    path("accounts/", include("rest_framework.urls", namespace="rest_framework")),
    path(
        "docs/",
        docs_view,
        name="schema-redoc",
    ),
    path(
        "swagger/",
        swagger_view,
        name="schema-swagger-ui",
    ),
    path("admin/", admin.site.urls),
]
