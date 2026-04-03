from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q

from catalog.models import Design
from marketing.models import DiscountCode
from marketing.tasks import check_and_issue_loyalty_discount
from .models import Order, OrderItem
from .forms import CheckoutForm


# ==========================================
# 1. CART & CHECKOUT VIEWS (Customer Facing)
# ==========================================

class AddToCartView(LoginRequiredMixin, View):
    """Handles adding a design to the user's pending cart with dynamic size pricing."""

    def post(self, request, design_id):
        design = get_object_or_404(Design, id=design_id)

        order, created = Order.objects.get_or_create(
            user=request.user,
            is_checked_out=False,
            defaults={'status': 'Pending'}
        )

        garment_type = request.POST.get('garment_type', 'T-Shirt')
        print_location = request.POST.get('print_location', 'front')
        color = request.POST.get('color', 'Black')
        size = request.POST.get('size', 'L')

        # --- DYNAMIC PRICING LOGIC ---
        final_price = design.price

        # 1. Garment Style Upcharge
        # NOTE: Make sure these strings exactly match what you typed in the Django Admin panel!
        if garment_type == 'Hoodie':
            final_price += Decimal('20.00')
        elif garment_type == 'Crewneck Sweatshirt':
            final_price += Decimal('15.00')

        # 2. Size Upcharge (Stacks on top of the style upcharge)
        if size == '2XL':
            final_price += Decimal('2.00')
        elif size == '3XL':
            final_price += Decimal('4.00')

        order_item, item_created = OrderItem.objects.get_or_create(
            order=order,
            design=design,
            garment_type=garment_type,
            color=color,
            size=size,
            print_location=print_location,
            defaults={'price': final_price, 'quantity': 1}
        )

        if not item_created:
            order_item.quantity += 1
            order_item.save()

        messages.success(request, f"'{design.title}' was added to your cart!")
        return redirect('cart-detail')

class CartDetailView(LoginRequiredMixin, TemplateView):
    """Displays the active cart items."""
    template_name = 'orders/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = Order.objects.filter(user=self.request.user, is_checked_out=False).first()

        if order and order.items.exists():
            items = order.items.all()
            subtotal = sum(item.price * item.quantity for item in items)

            # THE LOGIC: $3.99 shipping, free over $68.00
            shipping_cost = 0.00 if subtotal >= 68.00 else 3.99
            total = float(subtotal) + shipping_cost

            context['cart_items'] = items
            context['cart_subtotal'] = subtotal
            context['shipping_cost'] = shipping_cost
            context['cart_total'] = total

            # Tell the template exactly how much more they need for free shipping!
            context['amount_to_free_shipping'] = max(0, 68.00 - float(subtotal))
        else:
            context['cart_items'] = None
            context['cart_subtotal'] = 0.00
            context['shipping_cost'] = 0.00
            context['cart_total'] = 0.00

        return context

class UpdateCartItemView(LoginRequiredMixin, View):
    """Handles increasing, decreasing, or removing items directly from the cart."""

    def post(self, request, item_id):
        # 1. Securely fetch the item, ensuring it belongs to the active user's pending cart
        order_item = get_object_or_404(
            OrderItem,
            id=item_id,
            order__user=request.user,
            order__is_checked_out=False
        )

        # 2. Determine what button the user clicked
        action = request.POST.get('action')

        if action == 'increase':
            order_item.quantity += 1
            order_item.save()
            messages.success(request, f"Increased quantity of {order_item.design.title}.")

        elif action == 'decrease':
            # If quantity is 1, decreasing it should just delete the item entirely
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                messages.success(request, f"Decreased quantity of {order_item.design.title}.")
            else:
                order_item.delete()
                messages.success(request, "Item removed from cart.")

        elif action == 'remove':
            order_item.delete()
            messages.success(request, "Item removed from cart.")

        # 3. Bounce the user right back to the cart to see the updated total
        return redirect('cart-detail')

class CheckoutView(LoginRequiredMixin, UpdateView):
    """Handles checkout, shipping info, and loyalty discount application."""
    model = Order
    form_class = CheckoutForm
    template_name = 'orders/checkout.html'
    success_url = reverse_lazy('order-history')

    def get_object(self, queryset=None):
        return get_object_or_404(Order, user=self.request.user, is_checked_out=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        subtotal = sum(item.price * item.quantity for item in order.items.all())

        # Calculate for the visual summary on the checkout page
        shipping_cost = 0.00 if subtotal >= 68.00 else 3.99

        context['subtotal'] = subtotal
        context['shipping_cost'] = shipping_cost
        context['discount_amount'] = 0.00
        context['total'] = float(subtotal) + shipping_cost
        return context

    def form_valid(self, form):
        order = form.save(commit=False)
        subtotal = sum(item.price * item.quantity for item in order.items.all())

        # 1. Calculate Shipping
        shipping_cost = 0.00 if subtotal >= 68.00 else 3.99

        # 2. Calculate Discount
        discount_code_input = form.cleaned_data.get('discount_code')
        discount_amount = 0

        if discount_code_input:
            try:
                valid_code = DiscountCode.objects.get(
                    code=discount_code_input, user=self.request.user, is_active=True
                )
                discount_amount = float(subtotal) * (valid_code.discount_percentage / 100.0)
                valid_code.is_active = False
                valid_code.save()
                messages.success(self.request, "Loyalty discount applied successfully!")
            except DiscountCode.DoesNotExist:
                messages.error(self.request, "Invalid or expired discount code.")
                return self.form_invalid(form)

        # 3. Save the exact mathematical snapshot to the database
        order.shipping_cost = shipping_cost
        order.total_price = float(subtotal) - discount_amount + shipping_cost
        order.is_checked_out = True
        order.status = 'Pending'
        order.save()

        messages.success(self.request, "Your order has been placed successfully!")
        return super().form_valid(form)

class OrderHistoryView(LoginRequiredMixin, ListView):
    """Displays user's past finalized orders."""
    model = Order
    template_name = 'orders/order_history.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user,
            is_checked_out=True
        ).order_by('-created_at')


# ==========================================
# 2. ADMIN & BACKGROUND VIEWS (Staff Facing)
# ==========================================

# Added LoginRequiredMixin and UserPassesTestMixin to secure this view
class OrderFulfillmentView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Handles updating order status and triggering the Celery loyalty task."""
    model = Order
    fields = ['status']
    success_url = reverse_lazy('admin_order_list')

    # Ensure only staff members can access this URL
    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        response = super().form_valid(form)

        # If the admin just changed the status to 'Fulfilled', trigger Celery
        if self.object.status == 'Fulfilled':
            check_and_issue_loyalty_discount.delay(self.object.user.id)

        return response


class AdminOrderListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """A custom frontend dashboard for staff to view and search all placed orders."""
    model = Order
    template_name = 'orders/admin_order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        queryset = Order.objects.filter(is_checked_out=True).order_by('-created_at')

        # --- Search Logic ---
        query = self.request.GET.get('q')
        if query:
            # If they typed a number, search by exact Order ID
            if query.isdigit():
                queryset = queryset.filter(id=query)
            # Otherwise, search by customer username or email
            else:
                queryset = queryset.filter(
                    Q(user__username__icontains=query) |
                    Q(user__email__icontains=query)
                )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the search term back to the template so it stays in the search bar
        context['search_query'] = self.request.GET.get('q', '')
        return context

class AdminOrderDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Allows staff to see the full breakdown of a specific order."""
    model = Order
    template_name = 'orders/admin_order_detail.html'
    context_object_name = 'order'

    def test_func(self):
        return self.request.user.is_staff