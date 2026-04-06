from django.test import TestCase, Client
from core.forms import ContactUsForm


class ContactUsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.contact_url = '/contact/'

    def test_contact_page_loads_with_form(self):
        response = self.client.get(self.contact_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'How can we help you today?')

        if 'form' in response.context:
            self.assertIsInstance(response.context['form'], ContactUsForm)


class ContactUsFormTests(TestCase):
    def test_form_valid_data(self):
        form = ContactUsForm(data={
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'message': 'I have a question about my order and need some help tracking it.'
        })
        self.assertTrue(form.is_valid())

    def test_form_invalid_name_too_short(self):
        form = ContactUsForm(data={
            'name': 'Jo',
            'email': 'jane@example.com',
            'message': 'I have a question about my order and need some help tracking it.'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertEqual(
            form.errors['name'][0],
            "Please provide your full name (minimum 3 characters)."
        )

    def test_form_invalid_message_too_short(self):
        form = ContactUsForm(data={
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'message': 'Too short.'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)
        self.assertEqual(
            form.errors['message'][0],
            "Please provide a bit more detail (minimum 20 characters)."
        )

    def test_form_custom_clean_email(self):
        form = ContactUsForm(data={
            'name': 'Spam Bot',
            'email': 'bot@spam.com',
            'message': 'This is a spam message that is definitely long enough to pass.'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertEqual(
            form.errors['email'][0],
            "Please use a valid personal or business email."
        )