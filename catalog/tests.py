from django.test import TestCase, Client
from django.urls import reverse
from catalog.models import Design, Category


class CatalogTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.list_url = reverse('design-list')

        self.category = Category.objects.create(name="Apparel", slug="apparel")

        self.design1 = Design.objects.create(
            category=self.category,
            title="Cool Shirt",
            slug="cool-shirt",
            description="A very cool shirt.",
            price=25.00,
            is_featured=True
        )
        self.design2 = Design.objects.create(
            category=self.category,
            title="Awesome Hoodie",
            slug="awesome-hoodie",
            description="Warm and cozy.",
            price=45.00,
            is_featured=False
        )

    def test_design_creation(self):
        self.assertEqual(Design.objects.count(), 2)

    def test_design_str_method(self):
        self.assertEqual(str(self.design1), "Cool Shirt")

    def test_design_absolute_url(self):
        self.assertEqual(self.design1.get_absolute_url(), f'/design/{self.design1.slug}/')

    def test_design_list_view_loads(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cool Shirt")
        self.assertContains(response, "Awesome Hoodie")

    def test_design_detail_view(self):
        response = self.client.get(self.design1.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A very cool shirt.")

    def test_category_filter_functionality(self):
        response = self.client.get(self.list_url, {'category': 'apparel'})
        self.assertEqual(response.status_code, 200)