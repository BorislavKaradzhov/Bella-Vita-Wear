from django.db import models
from django.contrib.auth import get_user_model
from catalog.models import Design

User = get_user_model()

class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]

    design = models.ForeignKey(Design, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    content = models.TextField(max_length=500, help_text="Write your review here...")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevents a user from leaving multiple reviews on the same design
        unique_together = ('design', 'user')
        # Show newest reviews first
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.design.title} ({self.rating}/5 Stars)"