from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class DiscountCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.PositiveIntegerField(default=50)
    # Linking the code directly to the user so no one else can use it
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discount_codes')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.discount_percentage}% off for {self.user.username}"