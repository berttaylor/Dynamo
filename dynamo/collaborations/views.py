from django.forms import model_to_dict
from django.utils import timezone

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from collaborations.models import Collaboration, \
    CollaborationFile, CollaborationElement
from .serializers import CollaborationSerializer, \
    CollaborationFileSerializer, CollaborationElementSerializer


class CollaborationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Collaborations to be viewed and added
    """
    queryset = Collaboration.objects.all()
    lookup_field = 'slug'
    serializer_class = CollaborationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        We limit the queryset, so that the user sees collaboration from groups they are a part of
        We also limit by specific group, if a group slug is passed in the parameters.
        """

        # If group specified, we filter open requests by group and permission to approve
        if group_slug := self.request.query_params.get('group'):
            return Collaboration.objects.filter(
                related_group__members=self.request.user,
                related_group__slug=group_slug,
            )

        # If not we show open collaborations from all of the users groups
        return Collaboration.objects.filter(
            related_group__members=self.request.user,
        )


class CollaborationElementViewSet(CreateModelMixin,
                                  RetrieveModelMixin,
                                  ListModelMixin,
                                  GenericViewSet):
    """
    API endpoint that allows CollaborationElements to be viewed
    """
    queryset = CollaborationElement.objects.all()  # We change this later in get_queryset
    serializer_class = CollaborationElementSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = "reference"

    def get_queryset(self):
        """
        We limit the queryset, so that the user only sees tasks/milestones from the collaboration in the URL
        We also limit by specific group, if a group slug is passed in the parameters.
        """

        #  If a collaboration is specified, grab the slug
        if collaboration_slug := self.request.query_params.get('collaboration'):
            # Get collaboration and check it exists
            try:
                collaboration = Collaboration.objects.get(slug=collaboration_slug)
            except ObjectDoesNotExist:
                raise NotFound(detail="collaboration not found")
            else:
                # Check permissions, and deliver the information
                if self.request.user not in collaboration.related_group.members.all():
                    raise PermissionDenied(detail="Join this collaboration's group to see tasks")
                return CollaborationElement.objects.filter(collaboration=collaboration).order_by('position')

        # If no collaboration is specified, return all elements from all groups
        else:
            return self.queryset

    @action(detail=True, methods=['post'])
    def complete(self, request, reference=None):
        """
        Allows users to request to complete tasks
        """

        # Get  variables
        user, task = self.request.user, self.get_object()
        group = task.collaboration.related_group

        # If the user is not a member of the group, raise PermissionDenied
        if user not in group.members.all():
            raise PermissionDenied(detail="join this group to complete tasks")

        # If task is already completed, raise PermissionDenied
        if task.completed_at:
            raise PermissionDenied(detail=f"task already completed by {task.completed_by}")

        # If everything checks outs, assign the user to the completed_by field in the task,
        # and set the completed_at date to today.
        task.completed_at = timezone.now()
        task.completed_by = user

        # If the user added any completion notes in the post request, we add them to the object here.
        # If not, we set to None
        task.completion_notes = request.data.get('completion_notes', None)
        task.save()

        # Return a confirmation and code 200
        return Response(status=200,
                        data={
                            "name": task.name,
                            "completed_at": task.completed_at.strftime("%I:%M%p (%d %b '%y)"),
                            "completed_by": str(task.completed_by.username),
                            "completion_notes": str(task.completion_notes),
                            "reference": task.reference,
                            "collaboration": task.collaboration.name,
                        })


class CollaborationFileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows CollaborationFiles to be viewed
    """
    queryset = CollaborationFile.objects.all()
    serializer_class = CollaborationFileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
