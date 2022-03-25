from unittest import TestCase

from django.test import TransactionTestCase

from users.models import User


class UserTest(TransactionTestCase):

    def create_instance(self, first_name='test-user', last_name='test-user', password='12345', email="test@test.com"):
        return User.objects.create(first_name=first_name, last_name=last_name, password=password, email=email)

    def test_user_creation(self):
        w = self.create_instance()
        self.assertTrue(isinstance(w, User))
        self.assertEqual(User.objects.count(), 1)
