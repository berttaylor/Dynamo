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
    group_join_view,
    group_leave_view,
)
from .views_htmx import htmx_membership_list, htmx_membership_selector, htmx_membership_handler, htmx_announcement_list, \
    htmx_collaboration_list

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
        group_join_view,
        name="group-join",
    ),
    path(
        "<slug>/leave/",
        group_leave_view,
        name="group-leave",
    ),

    # HTMX views for the membership section of the group detail page.
    path(
        "htmx_membership_list/<group_id>/",
        htmx_membership_list,
        name="htmx_membership_list",
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

    # HTMX views for the announcement section of the group detail page.
    path(
        "htmx_announcement_list/<group_id>/",
        htmx_announcement_list,
        name="htmx_announcement_list",
    ),

    # HTMX views for the collaboration section of the group detail page.
    path(
        "htmx_collaboration_list/<group_id>/",
        htmx_collaboration_list,
        name="htmx_collaboration_list",
    ),

]
