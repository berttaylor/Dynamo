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

from django.urls import path
from groups.views import (
    GroupListView,
    GroupDetailView,
    GroupCreateView,
    GroupUpdateView,
    GroupDeleteView,
    GroupJoinView,
    GroupLeaveView,
    htmx_membership_selector,
    htmx_membership_handler,
    htmx_membership_view_handler,
)

urlpatterns = [
    path(
        "",
        GroupListView.as_view(),
        name="group-list",
    ),
    path(
        "create/",
        GroupCreateView.as_view(),
        name="group-create",
    ),
    path(
        "<slug>/",
        GroupDetailView.as_view(),
        name="group-detail",
    ),
    path(
        "<slug>/update/",
        GroupUpdateView.as_view(),
        name="group-update",
    ),
    path(
        "<slug>/delete/",
        GroupDeleteView.as_view(),
        name="group-delete",
    ),
    path(
        "<slug>/join/",
        GroupJoinView,
        name="group-join",
    ),
    path(
        "<slug>/leave/",
        GroupLeaveView,
        name="group-leave",
    ),

    # Views for the membership section of the group detail page.
    path(
        "htmx_membership_view_handler/<group_id>/",
        htmx_membership_view_handler,
        name="htmx_membership_view_handler",
    ),
    path(
        "htmx_membership_selector/<group_id>/<membership_id>/<membership_list_view>/",
        htmx_membership_selector,
        name="htmx_membership_selector",
    ),
    path(
        "htmx_membership_handler/<group_id>/<action>/<membership_list_view>/",
        htmx_membership_handler,
        name="htmx_membership_handler",
    ),
]
