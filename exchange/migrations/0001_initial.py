# Generated by Django 5.1.1 on 2024-09-23 07:49

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "phone_number",
                    models.CharField(db_index=True, max_length=11, unique=True),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Wallet",
            fields=[
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("coin", models.SmallIntegerField(choices=[(0, "USD"), (1, "Aban")])),
                ("balance", models.PositiveIntegerField(default=0)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="exchange.user"
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "coin")},
            },
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "status",
                    models.SmallIntegerField(
                        choices=[(0, "Pending"), (1, "Settled"), (2, "Cancelled")],
                        default=0,
                    ),
                ),
                ("amount", models.PositiveIntegerField()),
                (
                    "direction",
                    models.SmallIntegerField(choices=[(0, "Withdraw"), (1, "Deposit")]),
                ),
                (
                    "wallet",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="exchange.wallet",
                    ),
                ),
            ],
        ),
    ]
