from django.contrib import admin
from .models import Group, Membership, Post, Comment

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    # 'id' will show the UUID for each group
    list_display = ('id', 'name', 'slug', 'owner', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)} # Auto-fills slug as you type the name

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('id', 'group', 'user', 'joined_at')
    list_filter = ('group',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # 'id' will show the UUID for each post
    list_display = ('id', 'headline', 'author', 'group', 'created_at')
    list_filter = ('group', 'author')
    search_fields = ('headline', 'content')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'post', 'created_at')
    search_fields = ('content',)