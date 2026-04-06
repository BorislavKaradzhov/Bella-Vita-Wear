from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class AccountsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.profile_url = reverse('profile')

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Password123!'
        )

    def test_user_creation(self):
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')

    def test_unique_email_constraint(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='anotheruser',
                email='test@example.com',
                password='Password123!'
            )

    def test_user_str_method(self):
        self.assertEqual(str(self.user), 'testuser')

    def test_register_view_get(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

    def test_profile_requires_login(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(self.login_url))

    def test_profile_authenticated_access(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)

    def test_login_redirects_authenticated_users(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 302)

    def test_logout_user(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)


class LoginTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')

        self.user = User.objects.create_user(
            username='testuser',
            password='CorrectPassword123!'
        )

    def test_login_invalid_credentials_shows_error(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'WrongPassword999!'
        })

        self.assertEqual(response.status_code, 200)

        expected_error = "Please enter a correct username and password. Note that both fields may be case-sensitive."
        self.assertContains(response, expected_error)

        self.assertNotIn('_auth_user_id', self.client.session)

    def test_navbar_unauthenticated_visitor(self):
        self.client.logout()

        response = self.client.get(reverse('login'))

        self.assertContains(response, 'Login')
        self.assertContains(response, 'Register')
        self.assertContains(response, 'Contact Support')

        self.assertNotContains(response, 'My Orders')
        self.assertNotContains(response, 'Logout')
        self.assertNotContains(response, 'Staff Dashboard')
        self.assertNotContains(response, 'Add Design')

    def test_navbar_authenticated_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='regularbuyer',
            email='regularbuyer@bellavitawear.com',
            password='Password123!'
        )
        self.client.login(username='regularbuyer', password='Password123!')

        response = self.client.get(reverse('profile'))

        self.assertContains(response, 'Logout')
        self.assertContains(response, 'My Orders')
        self.assertContains(response, 'Cart')
        self.assertContains(response, 'Welcome, regularbuyer')

        self.assertNotContains(response, 'Login')
        self.assertNotContains(response, 'Register')
        self.assertNotContains(response, 'Staff Dashboard')
        self.assertNotContains(response, 'Add Design')