from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.CartDetailView.as_view(), name='cart-detail'),
    path('cart/add/<int:design_id>/', views.AddToCartView.as_view(), name='add-to-cart'),
    path('cart/update/<int:item_id>/', views.UpdateCartItemView.as_view(), name='update-cart-item'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('history/', views.OrderHistoryView.as_view(), name='order-history'),
# --- STAFF DASHBOARD URLS ---
    path('staff/orders/', views.AdminOrderListView.as_view(), name='admin_order_list'),
    path('staff/orders/<int:pk>/', views.AdminOrderDetailView.as_view(), name='admin_order_detail'),
    path('staff/orders/<int:pk>/fulfill/', views.OrderFulfillmentView.as_view(), name='order-fulfill'),
]