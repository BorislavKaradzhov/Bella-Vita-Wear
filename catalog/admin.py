from django.contrib import admin
from django.forms import CheckboxSelectMultiple
from django.db import models
from .models import Category, Design, DesignImage, GarmentType, Size, Color

# 1. Register the simple models so they can be populated with specific options
admin.site.register(GarmentType)
admin.site.register(Size)
admin.site.register(Color)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug')


# 2. Create the Inline for the Gallery Images
class DesignImageInline(admin.TabularInline):
    model = DesignImage
    extra = 3  # Provides 3 empty upload rows by default when editing a design


@admin.register(Design)
class DesignAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'is_featured', 'created_at')
    list_filter = ('category', 'is_featured', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('price', 'is_featured')

    # 3. Attach the image uploader directly to the Design edit page
    inlines = [DesignImageInline]

    # 4. Force all ManyToMany fields (Types, Sizes, Colors) to be checkboxes
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }