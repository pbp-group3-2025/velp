from django import template
from django.contrib.contenttypes.models import ContentType

register = template.Library()

@register.simple_tag
def content_type_id(obj):
    """Get the content type ID for a given object."""
    if obj is None:
        return ''
    return ContentType.objects.get_for_model(obj, for_concrete_model=False).id

@register.simple_tag
def get_content_type_id(model_name):
    """Get content type ID by model name."""
    try:
        return ContentType.objects.get(model=model_name.lower()).id
    except ContentType.DoesNotExist:
        return ''