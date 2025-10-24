import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify
from django.conf import settings  # for AUTH_USER_MODEL

# Create your models here.
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post_text = models.TextField(blank=True, null=True)
   
    def __str__(self):
        return self.post