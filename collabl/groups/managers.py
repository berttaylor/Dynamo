from django.db import models

import groups.constants as c

"""
A custom model manager that has a number of methods that can be called 
as filters on the Group model. This makes filtering clearer and more explicit, 
and means we can relocate the majority of the logic from our views.py files 
lower into the stack.
"""


class MembershipQuerySet(models.QuerySet):

    def pending(self):
        return self.filter(status=c.MEMBERSHIP_STATUS_PENDING)

    def current(self):
        return self.filter(status=c.MEMBERSHIP_STATUS_CURRENT)

    def ignored(self):
        return self.filter(status=c.MEMBERSHIP_STATUS_IGNORED)

    def admin(self):
        return self.filter(status=c.MEMBERSHIP_STATUS_ADMIN)

    def subscribers(self):
        return self.filter(is_subscribed=True)


class MembershipManager(models.Manager):
    """
    MembershipManager is a custom manager class used for filtering the Membership model.
    It's invoked as by_status = MembershipManager() on the model, which means
    that these custom methods can then be called in views as such:

    current_memberships = Membership.by_status.current()
    """

    def get_queryset(self):
        return MembershipQuerySet(self.model, using=self._db)

    def pending(self):
        return self.get_queryset().pending()

    def current(self):
        return self.get_queryset().current()

    def ignored(self):
        return self.get_queryset().ignored()

    def admin(self):
        return self.get_queryset().admin()

    def subscribers(self):
        return self.get_queryset().subscribers()
