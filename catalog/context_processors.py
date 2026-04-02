from .models import Category

def category_sidebar(request):
    # Ordering alphabetically ascending is handled by the model's Meta class
    categories = Category.objects.all()
    return {'sidebar_categories': categories}