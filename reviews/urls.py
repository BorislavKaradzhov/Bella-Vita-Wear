from django.urls import path
from . import views

urlpatterns = [
    path('design/<int:design_id>/', views.DesignReviewListAPIView.as_view(), name='api-design-reviews'),
]