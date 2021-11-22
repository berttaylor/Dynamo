"""msm_draft URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib.auth.views import LoginView, PasswordResetView, LogoutView
from django.urls import path, reverse_lazy
from django.views.generic import TemplateView
from dynamo import settings as s
from django.contrib.auth import views as django_auth_views

from users.views import SignUpView

urlpatterns = [
    path(
        "signup/",
        SignUpView,
        name="signup",
    ),
    path(
        "login/",
        LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    # The default configuration of password-reset sends a link without the port number (which is not valid in dev).
    # This one get the site domain from the env, which means it will work in both dev and prod.
    # The default configuration of password-reset sends a link without the port number (which is not valid in dev).
    # This one get the site domain from the env, which means it will work in both dev and prod.
    path(
        "password-reset/",
        PasswordResetView.as_view(
            template_name="registration/password_reset.html",
            html_email_template_name="templated_email/password_reset.email",
            subject_template_name="registration/password_reset_subject.txt",
            success_url=reverse_lazy("password_reset_requested"),
            extra_email_context={
                "site_url": str(s.SITE_PROTOCOL + s.SITE_DOMAIN),
            },
        ),
        name="password_reset",
    ),
    path(
        "password-reset-requested/",
        TemplateView.as_view(
            template_name="registration/password_reset_requested.html"
        ),
        name="password_reset_requested",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        django_auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        django_auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path(
        "password-change/",
        django_auth_views.PasswordChangeView.as_view(
            template_name="registration/password_change.html"
        ),
        name="password_change",
    ),
    path(
        "password-change-done/",
        django_auth_views.PasswordChangeDoneView.as_view(
            template_name="registration/password_change_done.html"
        ),
        name="password_change_done",
    ),
]
