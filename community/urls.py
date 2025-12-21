from django.urls import path
from . import views

app_name = "community"

urlpatterns = [
    path("", views.group_list, name="group_list"),


    path("groups/new/", views.create_group, name="create_group"),
    path("groups/<slug:slug>/edit/", views.edit_group, name="edit_group"),
    path("groups/<slug:slug>/delete/", views.delete_group, name="delete_group"),
    path("groups/<slug:slug>/join/", views.join_group, name="join_group"),
    path("groups/<slug:slug>/leave/", views.leave_group, name="leave_group"),
    path("groups/<slug:slug>/posts/new/", views.create_post, name="create_post"),
    path("groups/<slug:slug>/posts/<int:pk>/delete/", views.delete_post, name="delete_post"),
    path("groups/<slug:slug>/posts/<int:pk>/comments/new/", views.create_comment, name="create_comment"),
    path("groups/<slug:slug>/posts/<int:pk>/comments/<int:cpk>/delete/",views.delete_comment,name="delete_comment"),
    path("groups/<slug:slug>/posts/<int:pk>/", views.post_detail, name="post_detail"),
    path("groups/<slug:slug>/", views.group_detail, name="group_detail"),


    # AJAX endpoints for the flutter
    path("api/groups/", views.api_group_list, name="api_group_list"),
    path("api/groups/create/", views.api_create_group, name="api_create_group"),
    path("api/groups/<slug:slug>/", views.api_group_detail, name="api_group_detail"),
    path("api/groups/<slug:slug>/edit/", views.api_edit_group, name="api_edit_group"),
    path("api/groups/<slug:slug>/delete/", views.api_delete_group, name="api_delete_group"),
    path("api/groups/<slug:slug>/join/", views.api_join_group, name="api_join_group"),
    path("api/groups/<slug:slug>/leave/", views.api_leave_group, name="api_leave_group"),
    path("api/groups/<slug:slug>/posts/create/", views.api_create_post, name="api_create_post"),
    path("api/groups/<slug:slug>/posts/<int:pk>/", views.api_post_detail, name="api_post_detail"),
    path("api/groups/<slug:slug>/posts/<int:pk>/delete/", views.api_delete_post, name="api_delete_post"),
    path("api/groups/<slug:slug>/posts/<int:pk>/comments/create/", views.api_create_comment, name="api_create_comment"),
    path("api/groups/<slug:slug>/posts/<int:pk>/comments/<int:cpk>/delete/", views.api_delete_comment, name="api_delete_comment"),


    
]
