from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib import messages
from .forms import ContactUsForm

class ContactView(FormView):
    template_name = 'core/contact.html'
    form_class = ContactUsForm
    success_url = reverse_lazy('core:contact')

    def form_valid(self, form):
        messages.success(self.request, "Thank you! Your message has been sent to our support team.")
        return super().form_valid(form)