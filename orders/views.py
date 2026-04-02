from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy

from catalog.models import Design
from marketing.models import DiscountCode
from marketing.tasks import check_and_issue_loyalty_discount
from .models import Order, OrderItem
from .forms import CheckoutForm


# ==========================================
# 1. CART & CHECKOUT VIEWS (Customer Facing)
# ==========================================

class AddToCartView(LoginRequiredMixin, View):
    """Handles adding a design to the user's pending cart."""

    def post(self, request, design_id):
        design = get_object_or_404(Design, id=design_id)

        order, created = Order.objects.get_or_create(
            user=request.user,
            is_checked_out=False,
            defaults={'status': 'Pending'}
        )

        garment_type = request.POST.get('garment_type', 'TS')
        print_location = request.POST.get('print_location', 'front')
        color = request.POST.get('color', 'Black')
        size = request.POST.get('size', 'L')

        # We use get_or_create to prevent duplicate cart rows,
        # and we pull the accurate price directly from the design model.
        order_item, item_created = OrderItem.objects.get_or_create(
            order=order,
            design=design,
            garment_type=garment_type,
            color=color,
            size=size,
            print_location=print_location,
            defaults={'price': design.price, 'quantity': 1}
        )

        # If the exact same item is already in the cart, just increase the quantity
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

        if order:
            items = order.items.all()
            context['cart_items'] = items
            context['cart_total'] = sum(item.price * item.quantity for item in items)
        else:
            context['cart_items'] = None
            context['cart_total'] = 0.00

        return context


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

        context['subtotal'] = subtotal
        context['discount_amount'] = 0.00
        context['total'] = subtotal
        return context

    def form_valid(self, form):
        order = form.save(commit=False)
        subtotal = sum(item.price * item.quantity for item in order.items.all())
        discount_code_input = form.cleaned_data.get('discount_code')

        discount_amount = 0

        if discount_code_input:
            try:
                valid_code = DiscountCode.objects.get(
                    code=discount_code_input,
                    user=self.request.user,
                    is_active=True
                )
                discount_amount = float(subtotal) * (valid_code.discount_percentage / 100.0)
                valid_code.is_active = False
                valid_code.save()
                messages.success(self.request, "Loyalty discount applied successfully!")
            except DiscountCode.DoesNotExist:
                messages.error(self.request, "Invalid or expired discount code.")
                return self.form_invalid(form)

        order.total_price = float(subtotal) - discount_amount
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

    # FIX: Ensure only staff members can access this URL
    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        response = super().form_valid(form)

        # If the admin just changed the status to 'Fulfilled', trigger Celery
        if self.object.status == 'Fulfilled':
            check_and_issue_loyalty_discount.delay(self.object.user.id)

        return response