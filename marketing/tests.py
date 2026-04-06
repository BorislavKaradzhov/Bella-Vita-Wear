from django.test import TestCase
from django.contrib.auth import get_user_model
from orders.models import Order
from marketing.models import DiscountCode
from marketing.tasks import check_and_issue_loyalty_discount

User = get_user_model()

class MarketingTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='loyal', email='loyal@test.com', password='Password123!')

    def test_discount_code_str(self):
        code = DiscountCode.objects.create(code="TEST10", user=self.user, discount_percentage=10)
        self.assertEqual(str(code), f"TEST10 - 10% off for {self.user.username}")

    def test_loyalty_discount_issued_on_third_order(self):
        for _ in range(3):
            Order.objects.create(user=self.user, status='Fulfilled', is_checked_out=True)
        response = check_and_issue_loyalty_discount(self.user.id)
        self.assertIn("generated and emailed", response)
        self.assertEqual(DiscountCode.objects.filter(user=self.user).count(), 1)

    def test_loyalty_discount_not_issued_early(self):
        for _ in range(2):
            Order.objects.create(user=self.user, status='Fulfilled', is_checked_out=True)
        response = check_and_issue_loyalty_discount(self.user.id)
        self.assertIn("not eligible yet", response)
        self.assertEqual(DiscountCode.objects.filter(user=self.user).count(), 0)

    def test_loyalty_discount_issued_on_sixth_order(self):
        for _ in range(6):
            Order.objects.create(user=self.user, status='Fulfilled', is_checked_out=True)
        check_and_issue_loyalty_discount(self.user.id)
        self.assertEqual(DiscountCode.objects.filter(user=self.user).count(), 1)

    def test_loyalty_discount_invalid_user(self):
        response = check_and_issue_loyalty_discount(9999) # Non-existent ID
        self.assertEqual(response, "User not found.")

    def test_discount_default_active(self):
        code = DiscountCode.objects.create(code="AUTO50", user=self.user)
        self.assertTrue(code.is_active)