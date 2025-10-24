from django import template
from django.contrib.contenttypes.models import ContentType

register = template.Library()

@register.simple_tag
def content_type_id(obj):
    model = obj if isinstance(obj, type) else obj.__class__
    return ContentType.objects.get_for_model(model, for_concrete_model=False).pk

@register.filter
def model_name(obj):
    return getattr(obj._meta, "model_name", "-")

@register.simple_tag
def object_id(obj):
    return getattr(obj, "pk", None)