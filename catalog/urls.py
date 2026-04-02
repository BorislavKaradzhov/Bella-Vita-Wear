from django.urls import path
from . import views

urlpatterns = [
    path('', views.DesignListView.as_view(), name='design-list'),
    path('design/<slug:slug>/', views.DesignDetailView.as_view(), name='design-detail'),
    path('design/create/', views.DesignCreateView.as_view(), name='design-create'),
]