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

from chat.views_htmx import group_message_create_view, group_message_delete_view, group_message_update_view
from collaborations.views_htmx import group_collaboration_create_view
from groups.views import (
    GroupDetailView,
    group_join_view,
    group_leave_view, GroupSearchView,
)
from .views_htmx import group_update_view, group_image_view, group_membership_view, \
    group_membership_selector_view, group_membership_handler_view, group_announcement_list, group_announcement_delete, \
    group_announcement_create, group_announcement_update, group_collaboration_list, group_create_view

urlpatterns = [
    path(
        "create/",
        group_create_view,
        name="group-create",
    ),
    path(
        "find/",
        GroupSearchView.as_view(),
        name="group-search",
    ),
    path(
        "<slug>/",
        GroupDetailView.as_view(),
        name="group-detail",
    ),

    path(
        "<slug>/update",
        group_update_view,
        name="group-update",
    ),

    path(
        "<slug>/image",
        group_image_view,
        name="group-image",
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

    path(
        "<slug>/messages",
        group_message_create_view,
        name="group-message-create",
    ),
    path(
        "<slug>/messages/<pk>",
        group_message_update_view,
        name="group-message-update",
    ),
    path(
        "<slug>/messages/<pk>/delete",
        group_message_delete_view,
        name="group-message-delete",
    ),

    # HTMX views for the membership section of the group detail page.
    path(
        "<slug>/memberships/",
        group_membership_view,
        name="group-membership-list",
    ),
    path(
        "<slug>/membership-selector/<pk>/<membership_filter>/",
        group_membership_selector_view,
        name="group-membership-selector",
    ),
    path(
        "<slug>/membership-handler/<action>/<membership_filter>/",
        group_membership_handler_view,
        name="group-membership-handler",
    ),

    # HTMX views for the announcement section of the group detail page.
    path(
        "<slug>/announcements",
        group_announcement_list,
        name="group-announcement-list",
    ),
    path(
        "<slug>/announcements/create",
        group_announcement_create,
        name="group-announcement-create",
    ),
    path(
        "<slug>/announcements/<pk>",
        group_announcement_update,
        name="group-announcement-update",
    ),
    path(
        "<slug>/announcements/<pk>/delete",
        group_announcement_delete,
        name="group-announcement-delete",
    ),

    # HTMX views for the collaboration section of the group detail page.
    path(
        "<slug>/collaborations",
        group_collaboration_list,
        name="group-collaboration-list",
    ),
    path(
        "<slug>/collaborations/create",
        group_collaboration_create_view,
        name="group-collaboration-create",
    ),
]
