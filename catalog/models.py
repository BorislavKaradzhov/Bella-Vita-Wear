import uuid
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


# --- Attribute Models ---
class GarmentType(models.Model):
    name = models.CharField(max_length=50)  # e.g., T-Shirt, Hoodie

    def __str__(self): return self.name


class Size(models.Model):
    name = models.CharField(max_length=10)  # e.g., S, M, L, XL, 2XL, 3XL

    def __str__(self): return self.name


class Color(models.Model):
    name = models.CharField(max_length=50)  # e.g., White, Black, Navy Blue

    def __str__(self): return self.name


# --- Category Model ---
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# --- Design Model ---
class Design(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='designs')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # We keep the main image for the catalog grid
    image = models.ImageField(upload_to='designs/', blank=False, null=False)

    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Multi-Select options
    available_types = models.ManyToManyField(GarmentType, related_name='designs')
    available_sizes = models.ManyToManyField(Size, related_name='designs')
    available_colors = models.ManyToManyField(Color, related_name='designs')

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = base_slug
            while Design.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{uuid.uuid4().hex[:4]}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('design-detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title


# --- Multiple Images Model ---
class DesignImage(models.Model):
    # To link back to the main Design. If a Design is deleted, its gallery images are too.
    design = models.ForeignKey(Design, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='designs/gallery/')

    def __str__(self):
        return f"Gallery Image for {self.design.title}"