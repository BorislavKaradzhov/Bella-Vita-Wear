from django.shortcuts import render

from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Review
from .serializers import ReviewSerializer

class DesignReviewListAPIView(generics.ListAPIView):
    """
    API endpoint that allows anyone to view reviews for a specific design.
    URL pattern might look like: /api/reviews/design/<int:design_id>/
    """
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny] # Publicly accessible as per requirements

    def get_queryset(self):
        design_id = self.kwargs['design_id']
        return Review.objects.filter(design_id=design_id).order_by('-created_at')
