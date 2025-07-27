# Generated manually to fix Role model references

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_role"),
        ("relations", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="relation",
            name="role",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="core.role"
            ),
        ),
        migrations.AlterField(
            model_name="partner",
            name="role",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="core.role",
            ),
        ),
    ] 