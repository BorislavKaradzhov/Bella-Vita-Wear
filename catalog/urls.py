from django.urls import path
from . import views

urlpatterns = [
    path('', views.DesignListView.as_view(), name='design-list'),
    path('design/create/', views.DesignCreateView.as_view(), name='design-create'),
    path('design/<slug:slug>/edit/', views.DesignUpdateView.as_view(), name='design-update'),
    path('design/<slug:slug>/', views.DesignDetailView.as_view(), name='design-detail'),
    path('design/<slug:slug>/delete/', views.DesignDeleteView.as_view(), name='design-delete'),
    path('api/designs/', views.DesignListAPIView.as_view(), name='api-design-list'),
    path('api/designs/<slug:slug>/', views.DesignDetailAPIView.as_view(), name='api-design-detail'),
]