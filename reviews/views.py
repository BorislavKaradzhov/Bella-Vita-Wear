from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from catalog.models import Design
from .forms import ReviewForm
from orders.models import OrderItem
from django.views.generic import ListView, UpdateView, DeleteView
from django.urls import reverse_lazy

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

class UserReviewListView(LoginRequiredMixin, ListView):
    """Displays all reviews written by the currently logged-in user."""
    model = Review
    template_name = 'reviews/user_reviews.html'
    context_object_name = 'reviews'

    def get_queryset(self):
        # Only fetch reviews belonging to the active user
        return Review.objects.filter(user=self.request.user).order_by('-created_at')

class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Allows a user to edit their own review."""
    model = Review
    fields = ['rating', 'content']
    template_name = 'reviews/review_form.html'

    # Prevent users from editing other people's reviews
    def test_func(self):
        review = self.get_object()
        return self.request.user == review.user

    def get_success_url(self):
        messages.success(self.request, "Your review was updated successfully!")
        return reverse_lazy('reviews:my-reviews')

class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Allows a user to delete their own review."""
    model = Review
    template_name = 'reviews/review_confirm_delete.html'
    success_url = reverse_lazy('reviews:my-reviews')

    # Prevent users from deleting other people's reviews
    def test_func(self):
        review = self.get_object()
        return self.request.user == review.user

    def form_valid(self, form):
        messages.success(self.request, "Your review has been successfully deleted.")
        return super().form_valid(form)

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