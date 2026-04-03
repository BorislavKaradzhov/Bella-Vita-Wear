from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Automatically creates user groups and distinct permissions for the exam.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Setting up user groups and permissions...")

        # 1. Create the Groups
        content_managers, created_cm = Group.objects.get_or_create(name='Content Managers')
        fulfillment_team, created_ft = Group.objects.get_or_create(name='Fulfillment Team')

        # 2. Assign Permissions for Content Managers (Catalog App)
        # We give them full CRUD (Create, Read, Update, Delete) access to the catalog
        catalog_permissions = Permission.objects.filter(content_type__app_label='catalog')
        content_managers.permissions.set(catalog_permissions)
        self.stdout.write(self.style.SUCCESS(f"- 'Content Managers' group assigned {catalog_permissions.count()} catalog permissions."))

        # 3. Assign Permissions for Fulfillment Team (Orders App)
        # They can VIEW and CHANGE orders, but they CANNOT DELETE them.
        order_permissions = Permission.objects.filter(
            content_type__app_label='orders',
            codename__in=['view_order', 'change_order', 'view_orderitem']
        )
        fulfillment_team.permissions.set(order_permissions)
        self.stdout.write(self.style.SUCCESS(f"- 'Fulfillment Team' group assigned {order_permissions.count()} order permissions."))

        self.stdout.write(self.style.SUCCESS('✅ All groups and permissions successfully configured!'))