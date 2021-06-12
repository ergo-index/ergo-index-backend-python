from django.apps import AppConfig


class ErgoIndexFundAppConfig(AppConfig):
    name = 'ergo_index_fund_api'
    verbose_name = "Ergo Index Fund API"

    def ready(self):
        """
        Startup hook that gets called when the Django backend starts (or restarts).
        """
        pass
