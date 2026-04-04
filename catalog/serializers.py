from rest_framework import serializers
from .models import Design

class DesignSerializer(serializers.ModelSerializer):
    # StringRelatedField translates the IDs (e.g., [1, 2, 3]) into
    # the actual readable text names (e.g., ["L", "XL", "2XL"])
    category = serializers.StringRelatedField()
    available_types = serializers.StringRelatedField(many=True)
    available_sizes = serializers.StringRelatedField(many=True)
    available_colors = serializers.StringRelatedField(many=True)

    class Meta:
        model = Design
        # The fields to be exposed to the public API
        fields = [
            'id',
            'title',
            'slug',
            'category',
            'description',
            'price',
            'image',
            'is_featured',
            'available_types',
            'available_sizes',
            'available_colors'
        ]