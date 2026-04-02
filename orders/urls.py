from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.CartDetailView.as_view(), name='cart-detail'),
    path('cart/add/<int:design_id>/', views.AddToCartView.as_view(), name='add-to-cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('history/', views.OrderHistoryView.as_view(), name='order-history'),
]