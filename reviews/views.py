from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from catalog.models import Design
from .forms import ReviewForm
from orders.models import OrderItem

# --- DRF Imports ---
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Review
from .serializers import ReviewSerializer


# ==========================================
# FRONTEND VIEWS (Standard Django)
# ==========================================
class AddReviewView(LoginRequiredMixin, View):
    """Handles the HTML form submission when a user posts a review."""
    def post(self, request, design_id):
        design = get_object_or_404(Design, id=design_id)

        has_purchased = OrderItem.objects.filter(
            order__user=request.user,
            order__status='Fulfilled',
            design=design
        ).exists()

        if not has_purchased:
            messages.error(request, "You can only review designs that you have purchased and received.")
            return redirect('design-detail', slug=design.slug)

        form = ReviewForm(request.POST)

        if form.is_valid():
            if design.reviews.filter(user=request.user).exists():
                messages.error(request, "You have already reviewed this design.")
            else:
                review = form.save(commit=False)
                review.design = design
                review.user = request.user
                review.save()
                messages.success(request, "Thank you! Your review has been posted.")
        else:
            messages.error(request, "There was an error submitting your review.")

        return redirect('design-detail', slug=design.slug)


# ==========================================
# API VIEWS (Django REST Framework)
# ==========================================
class DesignReviewListAPIView(generics.ListAPIView):
    """API endpoint that returns a design's reviews as JSON data."""
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        design_id = self.kwargs['design_id']
        return Review.objects.filter(design_id=design_id).order_by('-created_at')