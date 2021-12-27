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

from chat.views import group_message_create_view, collaboration_message_create_view, group_message_delete_view, \
    collaboration_message_delete_view

urlpatterns = [
    path(
        "group/<group_uuid>",
        group_message_create_view,
        name="group-chat",
    ),
    path(
        "group/delete/<message_id>",
        group_message_delete_view,
        name="group-message-delete",
    ),
    path(
        "collaboration/<collaboration_uuid>",
        collaboration_message_create_view,
        name="collaboration-chat",
    ),
    path(
        "collaboration/delete/<message_id>",
        collaboration_message_delete_view,
        name="collaboration-message-delete",
    ),
]
