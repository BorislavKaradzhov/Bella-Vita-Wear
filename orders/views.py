from django.shortcuts import render

from django.views.generic import UpdateView
from django.urls import reverse_lazy
from .models import Order
from marketing.tasks import check_and_issue_loyalty_discount


class OrderFulfillmentView(UpdateView):
    model = Order
    fields = ['status']
    success_url = reverse_lazy('admin_order_list')

    def form_valid(self, form):
        response = super().form_valid(form)

        # If the admin just changed the status to 'Fulfilled'
        if self.object.status == 'Fulfilled':
            # Pass the user ID to the Celery task to run in the background
            check_and_issue_loyalty_discount.delay(self.object.user.id)

        return response