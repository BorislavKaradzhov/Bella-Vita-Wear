from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        # Imports and activates your signals when the server starts
        import accounts.signals