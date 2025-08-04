from django.db import models
from core.models import Tenant, AuditModel
from core.utilities import hex_color_validator


class BaseOption(AuditModel):
    """
    Abstract base model for selectable options across the system,
    like status, priority, category, etc.
    """

    label = models.CharField(max_length=100)
    translated_label = models.CharField(max_length=100, blank=True)
    use_translation = models.BooleanField(default=False)
    color = models.CharField(
        max_length=7,
        default="#6B7280",
        validators=[hex_color_validator]
    )
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

    class Meta:
        abstract = True
        ordering = ['sort_order', 'label']
        verbose_name = "Option"
        verbose_name_plural = "Options"

    def get_display_name(self):
        if self.use_translation and self.translated_label:
            return self.translated_label
        return self.label

    def __str__(self):
        return self.get_display_name()
