from django.contrib import admin

from exchange import models


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    pass


@admin.register(models.Wallet)
class WalletAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    pass


@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    pass
