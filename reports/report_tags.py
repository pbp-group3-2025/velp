from django import template
from django.contrib.contenttypes.models import ContentType

register = template.Library()

@register.simple_tag
def content_type_id(obj):
    return ContentType.objects.get_for_model(obj, for_concrete_model=False).id