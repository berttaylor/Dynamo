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
    CollaborationDeleteView, TaskCreateView, MilestoneCreateView
from groups.views import (
    GroupListView,
    GroupDetailView,
    GroupCreateView,
    GroupUpdateView,
    GroupDeleteView,
    GroupJoinView,
    GroupLeaveView,
    GroupRequestApproveView,
    GroupRequestDenyView,
)

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
        "collaboration/<collaboration_uuid>/create-task",
        TaskCreateView,
        name="task-create",
    ),
    path(
        "collaboration/<collaboration_uuid>/create-milesteone",
        MilestoneCreateView,
        name="milestone-create",
    ),
]
