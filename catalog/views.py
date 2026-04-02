from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Design, Category
from .forms import DesignForm

class DesignListView(ListView):
    model = Design
    template_name = 'catalog/design_list.html'
    context_object_name = 'designs'
    paginate_by = 6  # Show 6 designs per page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class DesignDetailView(DetailView):
    model = Design
    template_name = 'catalog/design_detail.html'
    context_object_name = 'design'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Suggest similar designs from the same category, excluding the current one
        current_design = self.object
        context['similar_designs'] = Design.objects.filter(
            category=current_design.category
        ).exclude(id=current_design.id)[:4]
        return context

class DesignCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Design
    form_class = DesignForm
    template_name = 'catalog/design_form.html'
    success_url = reverse_lazy('design-list')

    # Only admins/staff can create designs
    def test_func(self):
        return self.request.user.is_staff