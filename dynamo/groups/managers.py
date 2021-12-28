from django.db import models
from django.utils import timezone

"""
A custom model manager that has a number of methods that can be called 
as filters on the Survey model. This makes filtering clearer and more explicit, 
and means we can relocate the majority of the logic from our views.py files 
lower into the stack.

Note: Pattern used here specifies that each model has one managers, with multiple
methods - but it is also possible to use multiple managers per model too,
if that pattern makes more sense.
"""


class SurveyQuerySet(models.QuerySet):
    def live(self):
        """Returns all surveys that are published, and have a closing date of
        greater than or equal to today's date, in ascending order."""
        return (
            self.filter(published=True)
            # .filter(close_date_time__gte=datetime.datetime.today())
            # .filter(close_date_time__gte=timezone.localtime(timezone.now()).date())
            .filter(close_date_time__gte=timezone.now()).order_by("close_date_time")
        )

    def expired(self):
        """Returns all surveys that are published, and have a closing date of
        less than today's date, in descending order."""
        return (
            self.filter(published=True)
            # .filter(close_date_time__lt=datetime.datetime.today())
            # .filter(close_date_time__lt=timezone.localtime(timezone.now()).date())
            .filter(close_date_time__lt=timezone.now()).order_by("-close_date_time")
        )


class SurveyManager(models.Manager):
    """
    SurveyManager is a custom manager class used for filtering the Survey model.
    It's invoked as managed_surveys = SurveyManager() on the model, which means
    that these custom methods can then be called in views as such:

    model = Survey.managed_surveys.expired()
    """

    def get_queryset(self):
        return SurveyQuerySet(self.model, using=self._db)

    def live(self):
        return self.get_queryset().live()

    def expired(self):
        return self.get_queryset().expired()
