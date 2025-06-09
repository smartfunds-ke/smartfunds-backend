from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = 'Accounts Management'
    label = 'accounts'

    def ready(self):
        """
        Override the ready method to import signals and other modules
        that need to be initialized when the app is ready.
        """
        import apps.accounts.signals
        import apps.accounts.permissions
