from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from catalog.models import Design, Category
from orders.models import Order, OrderItem
from marketing.models import DiscountCode
from orders.forms import StaffOrderUpdateForm

User = get_user_model()


class OrdersTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username='buyer',
            email='buyer@test.com',
            password='Password123!'
        )
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@test.com',
            password='Password123!',
            is_staff=True
        )

        self.category = Category.objects.create(name="Apparel", slug="apparel")

        self.design = Design.objects.create(
            category=self.category,
            title="My Shirt",
            slug="my-shirt",
            price=20.00
        )

        self.cart_url = reverse('cart-detail')
        self.add_url = reverse('add-to-cart', args=[self.design.id])

    def test_order_str(self):
        order = Order.objects.create(user=self.user)
        self.assertEqual(str(order), f"Order #{order.id} - buyer - Pending")

    def test_order_item_str(self):
        order = Order.objects.create(user=self.user)
        item = OrderItem.objects.create(order=order, design=self.design, quantity=2, price=20.00)
        self.assertEqual(str(item), f"2x My Shirt (Order #{order.id})")

    def test_add_to_cart_creates_order(self):
        self.client.login(username='buyer', password='Password123!')
        self.client.post(self.add_url, {'garment_type': 'T-Shirt', 'size': 'L', 'color': 'Black'})
        self.assertEqual(Order.objects.filter(user=self.user, is_checked_out=False).count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)

    def test_add_to_cart_increases_quantity(self):
        self.client.login(username='buyer', password='Password123!')
        self.client.post(self.add_url, {'garment_type': 'T-Shirt', 'size': 'L', 'color': 'Black'})
        self.client.post(self.add_url, {'garment_type': 'T-Shirt', 'size': 'L', 'color': 'Black'})
        item = OrderItem.objects.first()
        self.assertEqual(item.quantity, 2)

    def test_cart_detail_view(self):
        self.client.login(username='buyer', password='Password123!')
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, 200)

    def test_shipping_cost_standard(self):
        self.client.login(username='buyer', password='Password123!')
        self.client.post(self.add_url, {'garment_type': 'T-Shirt', 'size': 'L', 'color': 'Black'})
        response = self.client.get(self.cart_url)
        self.assertEqual(response.context['shipping_cost'], 3.99)

    def test_shipping_cost_free(self):
        self.design.price = 70.00
        self.design.save()
        self.client.login(username='buyer', password='Password123!')
        self.client.post(self.add_url, {'garment_type': 'T-Shirt', 'size': 'L', 'color': 'Black'})
        response = self.client.get(self.cart_url)
        self.assertEqual(response.context['shipping_cost'], 0.00)

    def test_remove_cart_item(self):
        self.client.login(username='buyer', password='Password123!')
        self.client.post(self.add_url, {'garment_type': 'T-Shirt', 'size': 'L'})
        item = OrderItem.objects.first()
        self.client.post(reverse('update-cart-item', args=[item.id]), {'action': 'remove'})
        self.assertEqual(OrderItem.objects.count(), 0)

    def test_checkout_requires_login(self):
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 302)

    def test_checkout_auto_applies_loyalty_discount(self):
        self.client.login(username='buyer', password='Password123!')
        self.client.post(self.add_url, {'garment_type': 'T-Shirt', 'size': 'L'})
        code = DiscountCode.objects.create(code="AUTO50", user=self.user, discount_percentage=50)
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.context['discount_amount'], 10.00)

    def test_checkout_manual_discount_override(self):
        self.client.login(username='buyer', password='Password123!')
        order = Order.objects.create(user=self.user, is_checked_out=False)
        OrderItem.objects.create(order=order, design=self.design, quantity=1, price=100.00)

        auto_code = DiscountCode.objects.create(code="AUTO50", user=self.user, discount_percentage=50, is_active=True)
        manual_code = DiscountCode.objects.create(code="MANUAL10", user=self.user, discount_percentage=10,
                                                  is_active=True)

        payload = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@bellavitawear.com',
            'shipping_address': '123 Test St',
            'city': 'Testville',
            'postal_code': '12345',
            'country': 'USA',
            'discount_code': 'MANUAL10'
        }

        response = self.client.post(reverse('checkout'), payload)

        if response.status_code == 200 and 'form' in response.context:
            print("FORM ERRORS (Manual Override):", response.context['form'].errors)

        order.refresh_from_db()
        auto_code.refresh_from_db()
        manual_code.refresh_from_db()

        self.assertEqual(order.total_price, 90.00)
        self.assertFalse(manual_code.is_active)
        self.assertTrue(auto_code.is_active)

    def test_checkout_burns_auto_code(self):
        self.client.login(username='buyer', password='Password123!')
        order = Order.objects.create(user=self.user, is_checked_out=False)
        OrderItem.objects.create(order=order, design=self.design, quantity=1, price=100.00)

        auto_code = DiscountCode.objects.create(code="AUTO50", user=self.user, discount_percentage=50, is_active=True)

        payload = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@bellavitawear.com',
            'shipping_address': '123 Test St',
            'city': 'Testville',
            'postal_code': '12345',
            'country': 'USA',
            'discount_code': ''
        }

        response = self.client.post(reverse('checkout'), payload)

        if response.status_code == 200 and 'form' in response.context:
            print("FORM ERRORS (Auto Burn):", response.context['form'].errors)

        auto_code.refresh_from_db()
        self.assertFalse(auto_code.is_active)

    def test_non_staff_access_denied(self):
        self.client.login(username='buyer', password='Password123!')
        response = self.client.get(reverse('admin_order_list'))
        self.assertEqual(response.status_code, 403)

    def test_staff_access_allowed(self):
        self.client.login(username='staff', password='Password123!')
        response = self.client.get(reverse('admin_order_list'))
        self.assertEqual(response.status_code, 200)

    def test_order_history_view(self):
        self.client.login(username='buyer', password='Password123!')
        Order.objects.create(user=self.user, is_checked_out=True)
        response = self.client.get(reverse('order-history'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['orders']), 1)

    def test_staff_form_fulfilled_to_pending_error(self):
        order = Order.objects.create(user=self.user, status='Fulfilled', is_checked_out=True)

        form_data = {
            'order_id': f"#{order.pk}",
            'status': 'Pending'
        }

        form = StaffOrderUpdateForm(data=form_data, instance=order)

        self.assertFalse(form.is_valid())

        self.assertIn('status', form.errors)

        expected_error = "You cannot change a fulfilled order back to pending. Please use 'Cancelled' if necessary."
        self.assertEqual(form.errors['status'][0], expected_error)

    def test_staff_form_cancelled_to_pending_error(self):
        order = Order.objects.create(user=self.user, status='Cancelled', is_checked_out=True)

        form_data = {
            'order_id': f"#{order.pk}",
            'status': 'Pending'
        }

        form = StaffOrderUpdateForm(data=form_data, instance=order)

        self.assertFalse(form.is_valid())

        self.assertIn('status', form.errors)

        expected_error = "A cancelled order cannot be changed."
        self.assertEqual(form.errors['status'][0], expected_error)

    def test_staff_form_cancelled_to_fulfilled_error(self):
        order = Order.objects.create(user=self.user, status='Cancelled', is_checked_out=True)

        form_data = {
            'order_id': f"#{order.pk}",
            'status': 'Fulfilled'
        }

        form = StaffOrderUpdateForm(data=form_data, instance=order)

        self.assertFalse(form.is_valid())

        self.assertIn('status', form.errors)

        expected_error = "A cancelled order cannot be changed."
        self.assertEqual(form.errors['status'][0], expected_error)