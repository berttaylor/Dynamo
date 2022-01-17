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

from collaborations.views import CollaborationCreateView, CollaborationDetailView, CollaborationUpdateView, \
    CollaborationDeleteView, TaskUpdateView, MilestoneUpdateView
from .views_htmx import task_create_view, milestone_create_view, task_delete_view, milestone_delete_view, \
    htmx_task_status_update_view, htmx_get_element_list_view

urlpatterns = [
    # We use long URLs here because collaborations are created within groups and this probably make more sense
    # to the user in terms of data hierarchy.
    path(
        "groups/<group_slug>/create-collaboration/",
        CollaborationCreateView.as_view(),
        name="collaboration-create",
    ),
    path(
        "collaborations/<slug>/",
        CollaborationDetailView.as_view(),
        name="collaboration-detail",
    ),
    path(
        "collaborations/<slug>/update",
        CollaborationUpdateView.as_view(),
        name="collaboration-update",
    ),
    path(
        "collaborations/<slug>/delete",
        CollaborationDeleteView.as_view(),
        name="collaboration-delete",
    ),
    path(
        "collaboration/<collaboration_id>/create-task",
        task_create_view,
        name="task-create",
    ),
    path(
        "collaboration/<collaboration_id>/create-milesteone",
        milestone_create_view,
        name="milestone-create",
    ),
    path(
        "task/<pk>/update",
        TaskUpdateView.as_view(),
        name="task-update",
    ),
    path(
        "task-status/<pk>/<action>",
        htmx_task_status_update_view,
        name="htmx-task-status-update",
    ),
    path(
        "htmx_get_element_list/<collaboration_pk>",
        htmx_get_element_list_view,
        name="htmx-get-element-list",
    ),

    path(
        "milestone/<pk>/update",
        MilestoneUpdateView.as_view(),
        name="milestone-update",
    ),
    path(
        "task/<pk>/delete",
        task_delete_view,
        name="task-delete",
    ),
    path(
        "milestone/<pk>/delete",
        milestone_delete_view,
        name="milestone-delete",
    ),
]
