"""dynamo URL Configuration

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
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view
from rest_framework_simplejwt.views import TokenRefreshView

from chat.views import MessageViewSet
from dynamo.auth import CustomTokenObtainPairView
from collaborations.views import CollaborationViewSet, \
     CollaborationFileViewSet, CollaborationElementViewSet
from groups.views import GroupViewSet, GroupJoinRequestViewSet
from support.views import FAQViewSet, SupportMessageViewSet
from users.views import UserViewSet, UserRegisterView, PasswordUpdateView

urlpatterns = [
    # ADMIN
    path('admin/', admin.site.urls),

    # Register
    path("register", UserRegisterView.as_view(), name="register"),
    path("password-update", PasswordUpdateView.as_view(), name="password-update"),

    # JWT
    path(
        "token",
        CustomTokenObtainPairView.as_view(),
        name="token_obtain_pair",  # Our custom token authentication
    ),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),

    # Api Documentation
    # Route TemplateView to serve Swagger UI template.
    #   * Provide `extra_context` with view name of `SchemaView`.
    path('swagger-ui', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='swagger-ui'),

    # Use the `get_schema_view()` helper to add a `SchemaView` to project URLs.
    #   * `title` and `description` parameters are passed to `SchemaGenerator`.
    #   * Provide view name for use with `reverse()`.
    path('openapi', get_schema_view(
        title="Dynamo",
        description="Collaborative task manager",
        version="1.0.0"
    ), name='openapi-schema'),

]

router = DefaultRouter(trailing_slash=False,)

# Users
router.register(r"user", UserViewSet)

# FAQ + Support
router.register(r"faqs", FAQViewSet)
router.register(r"support-messages", SupportMessageViewSet)

# Groups
router.register(r"groups", GroupViewSet)
router.register(r"group-join-requests", GroupJoinRequestViewSet)

# Collaborations
router.register(r"collaborations", CollaborationViewSet)
router.register(r"collaboration-elements", CollaborationElementViewSet)
router.register(r"collaboration-files", CollaborationFileViewSet)

# Chat
router.register(r"messages", MessageViewSet)

# Add router URLs to URL patterns
urlpatterns += router.urls
