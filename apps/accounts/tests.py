from django.test import TestCase
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class AccountsTest(TestCase):
    def test_create_roles(self):
        admin = CustomUser.objects.create_user(username='admin_test', role='ADMIN', password='password123')
        officer = CustomUser.objects.create_user(username='officer_test', role='OFFICER', password='password123')
        member = CustomUser.objects.create_user(username='member_test', role='MEMBER', password='password123')

        self.assertTrue(admin.is_admin_user)
        self.assertTrue(officer.is_officer_user)
        self.assertTrue(member.is_member_user)
