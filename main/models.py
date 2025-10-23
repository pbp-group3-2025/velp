import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify
from django.conf import settings  # for AUTH_USER_MODEL

# Venue
class Venue(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    LEISURE_CHOICES = [
        ('pitch', 'Pitch'),
        ('stadium', 'Stadium'),
        ('sports_centre', 'Sports Centre'),
    ]


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CityName = models.CharField(max_length=255)
    StreetName = models.TextField()
    leisure = models.CharField(max_length=20, choices=LEISURE_CHOICES, default='pitch')
    name = models.TextField(blank=True, null=True)
   
    def __str__(self):
        return self.name


# Community
from django.db import models
from django.utils.text import slugify
from django.conf import settings  # for AUTH_USER_MODEL

class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Post(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_posts')
    content = models.TextField()
    image_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author} in {self.group}: {self.content[:30]}'

 
class Comment(models.Model):                               
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']  

    def __str__(self):
        return f'Comment by {self.author} on Post#{self.post_id}'

