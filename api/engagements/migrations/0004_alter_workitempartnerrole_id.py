# Generated by Django 5.1.5 on 2025-07-11 17:22

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("engagements", "0003_workitem_is_deleted_alter_activitylog_work_item"),
    ]

    operations = [
        migrations.AlterField(
            model_name="workitempartnerrole",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False
            ),
        ),
    ]
