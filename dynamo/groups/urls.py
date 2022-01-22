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
    GroupDetailView,
    GroupCreateView,
    GroupUpdateView,
    GroupDeleteView,
    group_join_view,
    group_leave_view, AnnouncementCreateView,
)
from .views_htmx import htmx_membership_list, htmx_membership_selector, htmx_membership_handler, htmx_announcement_list, \
    htmx_collaboration_list, htmx_announcement_delete

urlpatterns = [
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
        "htmx-membership-list/<group_id>/",
        htmx_membership_list,
        name="htmx-membership-list",
    ),
    path(
        "htmx-membership-selector/<group_id>/<membership_id>/<membership_filter>/",
        htmx_membership_selector,
        name="htmx-membership-selector",
    ),
    path(
        "htmx-membership-handler/<group_id>/<action>/<membership_filter>/",
        htmx_membership_handler,
        name="htmx-membership-handler",
    ),

    # HTMX views for the announcement section of the group detail page.
    path(
        "htmx-announcement-list/<group_id>/",
        htmx_announcement_list,
        name="htmx-announcement-list",
    ),
    path(
        "<slug>/announcement/",
        AnnouncementCreateView.as_view(),
        name="announcement-create",
    ),
    path(
        "htmx-announcement-list/<group_id>/<pk>/delete",
        htmx_announcement_delete,
        name="htmx-announcement-delete",
    ),

    # HTMX views for the collaboration section of the group detail page.
    path(
        "htmx-collaboration-list/<group_id>/",
        htmx_collaboration_list,
        name="htmx_collaboration_list",
    ),

]
