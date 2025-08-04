import django.core.validators
import django.db.models.deletion
import uuid
from django.db import migrations, models
import relations.utilities.validation_helpers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="WorkItem",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("created_by", models.UUIDField(blank=True, db_index=True, null=True)),
                ("updated_by", models.UUIDField(blank=True, db_index=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField()),
                ("deadline", models.DateTimeField(blank=True, null=True)),
                ("is_deleted", models.BooleanField(default=False)),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="work_items",
                        to="core.tenant",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Case",
            fields=[
                (
                    "workitem_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="engagements.workitem",
                    ),
                ),
                ("case_reference", models.CharField(max_length=100, unique=True)),
                ("legal_area", models.CharField(max_length=100)),
                ("court_date", models.DateField(blank=True, null=True)),
            ],
            options={
                "abstract": False,
            },
            bases=("engagements.workitem",),
        ),
        migrations.CreateModel(
            name="Job",
            fields=[
                (
                    "workitem_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="engagements.workitem",
                    ),
                ),
                ("job_code", models.CharField(blank=True, max_length=50, null=True)),
                (
                    "estimated_hours",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("engagements.workitem",),
        ),
        migrations.CreateModel(
            name="WorkItemCategory",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("created_by", models.UUIDField(blank=True, db_index=True, null=True)),
                ("updated_by", models.UUIDField(blank=True, db_index=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                ("label", models.CharField(max_length=100)),
                ("translated_label", models.CharField(blank=True, max_length=100)),
                ("use_translation", models.BooleanField(default=False)),
                (
                    "color",
                    models.CharField(
                        default="#6B7280",
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Enter a valid hex color code (e.g. #RRGGBB).",
                                regex="^#(?:[0-9a-fA-F]{3}){1,2}$",
                            )
                        ],
                    ),
                ),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.tenant"
                    ),
                ),
            ],
            options={
                "verbose_name": "Option",
                "verbose_name_plural": "Options",
                "ordering": ["sort_order", "label"],
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="workitem",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="category_work_items",
                to="engagements.workitemcategory",
            ),
        ),
        migrations.CreateModel(
            name="WorkItemPriority",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("created_by", models.UUIDField(blank=True, db_index=True, null=True)),
                ("updated_by", models.UUIDField(blank=True, db_index=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                ("label", models.CharField(max_length=100)),
                ("translated_label", models.CharField(blank=True, max_length=100)),
                ("use_translation", models.BooleanField(default=False)),
                (
                    "color",
                    models.CharField(
                        default="#6B7280",
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Enter a valid hex color code (e.g. #RRGGBB).",
                                regex="^#(?:[0-9a-fA-F]{3}){1,2}$",
                            )
                        ],
                    ),
                ),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.tenant"
                    ),
                ),
            ],
            options={
                "verbose_name": "Option",
                "verbose_name_plural": "Options",
                "ordering": ["sort_order", "label"],
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="workitem",
            name="priority",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="priority_work_items",
                to="engagements.workitempriority",
            ),
        ),
        migrations.CreateModel(
            name="WorkItemStatus",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("created_by", models.UUIDField(blank=True, db_index=True, null=True)),
                ("updated_by", models.UUIDField(blank=True, db_index=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                ("label", models.CharField(max_length=100)),
                ("translated_label", models.CharField(blank=True, max_length=100)),
                ("use_translation", models.BooleanField(default=False)),
                (
                    "color",
                    models.CharField(
                        default="#6B7280",
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Enter a valid hex color code (e.g. #RRGGBB).",
                                regex="^#(?:[0-9a-fA-F]{3}){1,2}$",
                            )
                        ],
                    ),
                ),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.tenant"
                    ),
                ),
            ],
            options={
                "verbose_name": "Option",
                "verbose_name_plural": "Options",
                "ordering": ["sort_order", "label"],
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="workitem",
            name="status",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="status_work_items",
                to="engagements.workitemstatus",
            ),
        ),
        migrations.CreateModel(
            name="Ticket",
            fields=[
                (
                    "workitem_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="engagements.workitem",
                    ),
                ),
                (
                    "ticket_number",
                    models.CharField(
                        blank=True,
                        editable=False,
                        max_length=50,
                        null=True,
                        unique=True,
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["ticket_number"], name="engagements_ticket__d0834a_idx"
                    )
                ],
            },
            bases=("engagements.workitem",),
        ),
        migrations.CreateModel(
            name="Attachment",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("created_by", models.UUIDField(blank=True, db_index=True, null=True)),
                ("updated_by", models.UUIDField(blank=True, db_index=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                ("file", models.FileField(upload_to="case_attachments/")),
                ("filename", models.CharField(max_length=255)),
                ("file_size", models.IntegerField()),
                ("mime_type", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="core.tenant",
                    ),
                ),
                (
                    "work_item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="engagements.workitem",
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["tenant"], name="engagements_tenant__2c289f_idx"
                    ),
                    models.Index(
                        fields=["work_item"], name="engagements_work_it_4a0ab0_idx"
                    ),
                    models.Index(
                        fields=["filename"], name="engagements_filenam_bd370d_idx"
                    ),
                    models.Index(
                        fields=["created_by"], name="engagements_created_1d4caa_idx"
                    ),
                    models.Index(
                        fields=["created_at"], name="engagements_created_3dabe6_idx"
                    ),
                    models.Index(
                        fields=["tenant", "work_item"],
                        name="engagements_tenant__5b9c3c_idx",
                    ),
                    models.Index(
                        fields=["tenant", "created_by"],
                        name="engagements_tenant__7716a1_idx",
                    ),
                ],
            },
            bases=(
                models.Model,
                relations.utilities.validation_helpers.TenantValidatorMixin,
            ),
        ),
        migrations.CreateModel(
            name="Comment",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("created_by", models.UUIDField(blank=True, db_index=True, null=True)),
                ("updated_by", models.UUIDField(blank=True, db_index=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                ("content", models.TextField()),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="core.tenant",
                    ),
                ),
                (
                    "work_item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="engagements.workitem",
                    ),
                ),
            ],
            options={
                "ordering": ["created_at"],
                "indexes": [
                    models.Index(
                        fields=["tenant"], name="engagements_tenant__d509b2_idx"
                    ),
                    models.Index(
                        fields=["work_item"], name="engagements_work_it_eff6ac_idx"
                    ),
                    models.Index(
                        fields=["created_by"], name="engagements_created_779d71_idx"
                    ),
                    models.Index(
                        fields=["created_at"], name="engagements_created_fe993f_idx"
                    ),
                    models.Index(
                        fields=["tenant", "work_item"],
                        name="engagements_tenant__81cca4_idx",
                    ),
                    models.Index(
                        fields=["tenant", "created_by"],
                        name="engagements_tenant__7e10c5_idx",
                    ),
                ],
            },
            bases=(
                models.Model,
                relations.utilities.validation_helpers.TenantValidatorMixin,
            ),
        ),
        migrations.AddIndex(
            model_name="workitem",
            index=models.Index(
                fields=["tenant"], name="engagements_tenant__d01a32_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="workitem",
            index=models.Index(
                fields=["status"], name="engagements_status__56f047_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="workitem",
            index=models.Index(
                fields=["category"], name="engagements_categor_37925b_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="workitem",
            index=models.Index(
                fields=["priority"], name="engagements_priorit_158efd_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="workitem",
            index=models.Index(
                fields=["created_by"], name="engagements_created_e8c985_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="workitem",
            index=models.Index(
                fields=["is_deleted"], name="engagements_is_dele_bfbc8c_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="workitem",
            index=models.Index(
                fields=["created_at"], name="engagements_created_f6f079_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="workitem",
            index=models.Index(
                fields=["deadline"], name="engagements_deadlin_5fa081_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="workitem",
            index=models.Index(
                fields=["tenant", "status"], name="engagements_tenant__f338eb_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="workitem",
            index=models.Index(
                fields=["tenant", "category"], name="engagements_tenant__aa07a1_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="workitem",
            index=models.Index(
                fields=["tenant", "priority"], name="engagements_tenant__e1fc24_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="workitem",
            index=models.Index(
                fields=["tenant", "is_deleted"], name="engagements_tenant__fc5549_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="workitem",
            index=models.Index(
                fields=["status", "priority"], name="engagements_status__b64202_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="workitem",
            index=models.Index(
                fields=["category", "status"], name="engagements_categor_b5a341_idx"
            ),
        ),
    ]
