from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet

from .serializers import FAQSerializer, SupportMessageSerializer
from support.models import FAQ, SupportMessage


class FAQViewSet(ReadOnlyModelViewSet):
    """
    API endpoint that allows FAQ questions/answers to be viewed - they are added via the django admin.
    """
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]


class SupportMessageViewSet(CreateModelMixin, GenericViewSet):
    """
    API endpoint that allows SupportMessages to be create only (not viewed - this is handled in django admin)
    """
    queryset = SupportMessage.objects.all()
    serializer_class = SupportMessageSerializer
    permission_classes = [AllowAny]