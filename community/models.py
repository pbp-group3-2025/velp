from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_groups",
        null=True, blank=True,   
    )

    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

  #Difrrentiate owner and member
    def is_owner(self, user):
        return bool(self.owner_id and user and user.is_authenticated and user.id == self.owner_id)

    def is_member(self, user):
        if not user or not user.is_authenticated:
            return False
        if self.is_owner(user):
            return True
        return self.memberships.filter(user=user).exists()

    def __str__(self):
        return self.name


class Membership(models.Model):
    #Becomes a member of a group
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_memberships")
    joined_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        unique_together = ("group", "user")

    def __str__(self):
        return f"{self.user} in {self.group}"


class Post(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_posts')
    headline = models.CharField(max_length=255, default='', blank=False)
    content = models.TextField()
    image_url = models.URLField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ['-created_at']

    def can_delete(self, user):
        if not user or not getattr(user, "is_authenticated", False):
            return False
        return user.id == self.author_id or user.id == self.group.owner_id
    def __str__(self):
        return f'{self.author} in {self.group}: {self.headline or self.content[:30]}'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_comments')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author} on Post#{self.post_id}'
    # Determine if a user can delete this comment/ Owner of post or author of comment
    def can_delete(self, user):
        if not user or not user.is_authenticated:
            return False
        return user.id == self.author_id or user.id == self.post.group.owner_id
