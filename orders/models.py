from django.db import models
from django.contrib.auth import get_user_model
from catalog.models import Design

User = get_user_model()


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Fulfilled', 'Fulfilled'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    is_checked_out = models.BooleanField(default=False)
    shipping_address = models.TextField()

    # Keep a permanent record of the shipping cost applied to this order
    shipping_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - {self.status}"

    @property
    def subtotal(self):
        return sum(item.price * item.quantity for item in self.items.all())

    @property
    def discount_amount(self):
        if self.total_price:
            discount = float(self.subtotal) + float(self.shipping_cost) - float(self.total_price)

            return round(max(0.00, discount), 2)
        return 0.00

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    # If a design is deleted from the catalog, we don't want to delete the order history
    design = models.ForeignKey(Design, on_delete=models.SET_NULL, null=True)

    # Storing the exact choices the customer made at checkout
    garment_type = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=5)
    print_location = models.CharField(max_length=10)  # e.g., 'front' or 'back'

    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        design_title = self.design.title if self.design else "Deleted Design"
        return f"{self.quantity}x {design_title} (Order #{self.order.id})"

    @property
    def total_price(self):
        return self.price * self.quantity