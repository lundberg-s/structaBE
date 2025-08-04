from django.core.validators import RegexValidator

hex_color_validator = RegexValidator(
    regex=r"^#(?:[0-9a-fA-F]{3}){1,2}$",
    message="Enter a valid hex color code (e.g. #RRGGBB)."
)
