from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import UserSerializer, UserRegisterSerializer, PasswordUpdateSerializer
from users.models import User

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnUserAccountOrReadOnly(BasePermission):
    """
    Custom permission that checks that the requesting user is the owner of the
    user account when an edit request is made.
    """
    message = 'You cannot edit this user.'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj == request.user


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsOwnUserAccountOrReadOnly, ]
    http_method_names = ["get", "put", "patch"]


class UserRegisterView(CreateAPIView):
    """
    API endpoint that allows users to register
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegisterSerializer


class PasswordUpdateView(UpdateAPIView):
    """
    API endpoint that allows users to change their password
    """

    serializer_class = PasswordUpdateSerializer

    model = User

    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):

        # Get user instance and serialize data
        user = self.request.user
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():

            # Check that the old password matches the has stored in db
            if not user.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            # hash the new password and save
            user.set_password(serializer.data.get("new_password"))
            user.save()

            # Send a simple API response
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated.',
                'data': []
            }

            return Response(response)

        # If the data is not valid, return 400
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
