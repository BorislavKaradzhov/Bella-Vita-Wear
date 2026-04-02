from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from catalog.models import Design

User = get_user_model()


class Review(models.Model):
    # Link to the user who wrote the review
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')

    # Link to the specific design being reviewed
    design = models.ForeignKey(Design, on_delete=models.CASCADE, related_name='reviews')

    # Rating out of 5 stars
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Enter a rating between 1 (lowest) and 5 (highest)."
    )

    comment = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Show newest reviews first
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.username} for {self.design.title} ({self.rating}/5)"