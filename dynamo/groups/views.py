from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from groups.models import Group, GroupJoinRequest
from .serializers import GroupJoinRequestSerializer, \
    GroupSerializer, GroupDetailSerializer
import groups.constants as c


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing groups
    """
    queryset = Group.objects.all()
    lookup_field = 'slug'
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self, *args, **kwargs):
        if self.action == "list":
            return GroupSerializer
        return GroupDetailSerializer

    @action(detail=True, methods=['post'])
    def join(self, request, slug=None):
        """
        Allows users to request to join groups.
        """

        # Get  variables
        user, group = self.request.user, self.get_object()

        # If the user is already a member, raise 409 (for conflict)
        if user in group.members.all():
            return Response(status=409, data={"message": "You are already a member of this group"})
        # If the user has already requested to join, raise 409 (for conflict)
        elif GroupJoinRequest.objects.filter(user=user, group=group).exists():
            return Response(status=409, data={"message": "Duplicate Request"})
        # If the user isn't in the group, and no outstanding request exists, create one.
        else:
            group_join_request = GroupJoinRequest.objects.create(user=user, group=group)
            return Response(status=201, data={"message": "Request Submitted", "pk": group_join_request.pk})

    @action(detail=True, methods=['post'])
    def leave(self, request, slug=None):
        """
        Allows users to leave groups
        """

        # Get  variables
        user, group = self.request.user, self.get_object()

        # If the user id not a member of the group, raise 409 (for conflict)
        if user not in group.members.all():
            return Response(status=409, data="You are already a member of this group")
        # else, remove them
        else:
            group.members.remove(user)
            group.subscribers.remove(user)
            group.admins.remove(user)
            return Response(status=200, data="You have left the group")


class GroupJoinRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows GroupJoinRequests to be approved/denied, adn viewed
    NOTE: GroupJoinRequests are created using the 'join' action on the groups detail page.
    """
    queryset = GroupJoinRequest.objects.all()
    serializer_class = GroupJoinRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        We limit the queryset, so that the user sees only requests that:
            A) They have permission to handle (they must be an admin for the target group to approve/deny the request)
            B) Have not been handled (there is no reason for the user to see requests that are already approved/denied)
            C) Are for the group specified in the URL (If a group is specified)
        """

        # If group specified, we filter open requests by group and permission to approve
        if group_slug := self.request.query_params.get('group'):
            return GroupJoinRequest.objects.filter(
                handled_date__isnull=True,
                group__admins=self.request.user,
                group__slug=group_slug
            )

        # If not we show all open requests that the user has permission to approve
        return GroupJoinRequest.objects.filter(
            handled_date__isnull=True,
            group__admins=self.request.user
        )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Allows admins to approve requests
        """

        # Get  variables
        handling_user = self.request.user
        join_request = self.get_object()
        requesting_user = join_request.user
        target_group = join_request.group

        # If the user is not an admin of the group, they cannot approve requests
        if handling_user not in target_group.admins.all():
            raise PermissionDenied

        # else, process the request
        else:
            target_group.members.add(requesting_user)
            target_group.subscribers.add(requesting_user)
            join_request.status = c.REQUEST_STATUS_APPROVED
            join_request.handled_by = handling_user
            join_request.handled_date = timezone.now()
            join_request.save()
            return Response(status=200, data=f"{requesting_user}'s request to join '{target_group}' was approved")

    @action(detail=True, methods=['post'])
    def deny(self, request, pk=None):
        """
        Allows admins to deny requests
        """

        # Get  variables
        handling_user = self.request.user
        join_request = self.get_object()
        requesting_user = join_request.user
        target_group = join_request.group

        # If the user is not an admin of the group, they cannot approve requests
        if handling_user not in target_group.admins.all():
            raise PermissionDenied

        # else, process the request
        else:
            join_request.status = c.REQUEST_STATUS_DENIED
            join_request.handled_by = handling_user
            join_request.handled_date = timezone.now()
            join_request.save()
            return Response(status=200, data=f"'{requesting_user}''s request to join '{target_group}' was denied")