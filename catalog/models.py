from django.db import models
from django.core.validators import MinLengthValidator


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']  # Automatically orders A-Z for the sidebar

    def __str__(self):
        return self.name


class GarmentAttribute(models.Model):
    GARMENT_TYPES = [
        ('TS', 'T-Shirt'),
        ('HD', 'Hoodie'),
        ('CN', 'Crewneck'),
    ]
    garment_type = models.CharField(max_length=2, choices=GARMENT_TYPES)
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=5)  # e.g., S, M, L, XL, XXL

    def __str__(self):
        return f"{self.get_garment_type_display()} - {self.color} - {self.size}"


class Design(models.Model):
    title = models.CharField(max_length=150, validators=[MinLengthValidator(3)])
    image = models.ImageField(upload_to='designs/')
    description = models.TextField()

    # Many-to-One Relationship (A design belongs to one category, a category has many designs)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='designs')

    # Many-to-Many Relationship (A design can be printed on many garments, a garment can have many designs)
    available_garments = models.ManyToManyField(GarmentAttribute, related_name='designs')

    def __str__(self):
        return self.title