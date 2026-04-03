from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    # Make below fields read-only so staff can't accidentally change a customer's historical receipt!
    readonly_fields = ('design', 'garment_type', 'size', 'color', 'print_location', 'price', 'quantity')

    # Prevents staff from deleting individual items off an already-placed order
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 'created_at', 'is_checked_out')
    list_filter = ('status', 'is_checked_out', 'created_at')
    search_fields = ('user__username', 'shipping_address', 'id')

    # Allows admins to change the status directly from the list view
    # without even having to click into the order!
    list_editable = ('status',)

    readonly_fields = ('user', 'shipping_address', 'shipping_cost', 'total_price', 'is_checked_out', 'created_at',
                       'updated_at')
    inlines = [OrderItemInline]