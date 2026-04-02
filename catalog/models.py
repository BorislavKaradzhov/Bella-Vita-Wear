import uuid
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinLengthValidator

class GarmentAttribute(models.Model):
    GARMENT_TYPES = [
        ('TS', 'T-Shirt'),
        ('HD', 'Hoodie'),
        ('CN', 'Crewneck'),
    ]
    garment_type = models.CharField(max_length=2, choices=GARMENT_TYPES)
    # 1. Makes title optional so it doesn't have to be manually typed
    title = models.CharField(max_length=200, blank=True)
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=5)  # e.g., S, M, L, XL, XXL

    # 2. Auto-generate the title before saving
    def save(self, *args, **kwargs):
        if not self.title:
            # e.g., "Hoodie - Red - L"
            self.title = f"{self.get_garment_type_display()} - {self.color} - {self.size}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_garment_type_display()} - {self.color} - {self.size}"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']  # Automatically orders A-Z for the sidebar

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Design(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='designs')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='designs/', blank=False, null=False)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    available_garments = models.ManyToManyField(GarmentAttribute, related_name='designs')

    def save(self, *args, **kwargs):
        if not self.slug:
            # First, generate the base slug
            base_slug = slugify(self.title)
            self.slug = base_slug

            # Check if this slug already exists in the database
            # We use a loop in case the first random suffix also exists
            while Design.objects.filter(slug=self.slug).exists():
                # Append a 4-character unique hex string (e.g., -a1b2)
                self.slug = f"{base_slug}-{uuid.uuid4().hex[:4]}"

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('design-detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title