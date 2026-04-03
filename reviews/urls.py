from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    # Frontend URL (For customers submitting the HTML Form)
    path('add/<int:design_id>/', views.AddReviewView.as_view(), name='add_review'),

    # API URL (For external apps requesting JSON Data)
    path('design/<int:design_id>/', views.DesignReviewListAPIView.as_view(), name='api-design-reviews'),
]