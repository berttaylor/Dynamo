"""URL Configuration

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
from collabl import settings as s
from django.contrib.auth import views as django_auth_views

from users.forms import CustomLoginForm, CustomPasswordResetForm
from users.views import (
    sign_up_view,
    UserUpdateView,
    UserGroupListView,
    UserCollaborationListView,
    account_activation_view,
)

urlpatterns = [
    path(
        "accounts/signup/",
        sign_up_view,
        name="signup",
    ),
    path(
        "login/",
        LoginView.as_view(
            template_name="landing/registration/signin.html",
            form_class=CustomLoginForm,
            success_url=reverse_lazy("group-search"),
        ),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    # The default configuration of password-reset sends a link without the port number (which is not valid in dev).
    # This one get the site domain from the env, which means it will work in both dev and prod.
    # The default configuration of password-reset sends a link without the port number (which is not valid in dev).
    # This one get the site domain from the env, which means it will work in both dev and prod.
    path(
        "accounts/password-reset/",
        PasswordResetView.as_view(
            form_class=CustomPasswordResetForm,
            template_name="landing/registration/password_reset.html",
            html_email_template_name="templated_email/password_reset.email",
            subject_template_name="registration/password_reset_subject.txt",
            success_url=reverse_lazy("password-reset-requested"),
            extra_email_context={
                "site_url": str(s.SITE_PROTOCOL + s.SITE_DOMAIN),
            },
        ),
        name="password-reset",
    ),
    path(
        "accounts/password-reset-requested/",
        TemplateView.as_view(
            template_name="landing/registration/password_reset_requested.html"
        ),
        name="password-reset-requested",
    ),
    path(
        "accounts/password-reset-confirm/<uidb64>/<token>/",
        django_auth_views.PasswordResetConfirmView.as_view(
            template_name="landing/registration/password_reset_confirm.html"
        ),
        name="password-reset-confirm",
    ),
    path(
        "accounts/password-reset-complete/",
        django_auth_views.PasswordResetCompleteView.as_view(
            template_name="landing/registration/password_reset_complete.html"
        ),
        name="password-reset-complete",
    ),
    path(
        "accounts/password-change/",
        django_auth_views.PasswordChangeView.as_view(
            template_name="landing/registration/password_change.html"
        ),
        name="password-change",
    ),
    path(
        "accounts/password-change-done/",
        django_auth_views.PasswordChangeDoneView.as_view(
            template_name="landing/registration/password_change_done.html"
        ),
        name="password-change-done",
    ),
    path("activate/<encoded_pk>/<token>", account_activation_view, name="activate"),
    # Home views
    path(
        "user/details/",
        UserUpdateView.as_view(),
        name="user-update",
    ),
    path(
        "user/groups/",
        UserGroupListView.as_view(),
        name="user-group-list",
    ),
    path(
        "user/collaborations/",
        UserCollaborationListView.as_view(),
        name="user-collaboration-list",
    ),
]
