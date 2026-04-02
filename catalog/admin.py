from django.contrib import admin
from django.forms import CheckboxSelectMultiple
from django.db import models
from .models import Category, Design, GarmentAttribute


# 1. Register GarmentAttribute so you can add "Small", "Medium", etc.
@admin.register(GarmentAttribute)
class GarmentAttributeAdmin(admin.ModelAdmin):
    list_display = ('title',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug')


@admin.register(Design)
class DesignAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'is_featured', 'created_at')
    list_filter = ('category', 'is_featured', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('price', 'is_featured')

    # 2. Force ManyToMany fields to render as Checkboxes
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }