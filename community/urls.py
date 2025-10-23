from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('', views.group_list, name='group_list'),


    path('groups/new/', views.create_group, name='create_group'),         
    path('groups/<slug:slug>/new/', views.create_post, name='create_post'),
    path('groups/<slug:slug>/', views.group_detail, name='group_detail'),
    path('groups/<slug:slug>/posts/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('groups/<slug:slug>/delete/', views.delete_group, name='delete_group'),
    path('groups/<slug:slug>/posts/<int:pk>/comments/new/', views.create_comment, name='create_comment'),  
    path('groups/<slug:slug>/edit/', views.edit_group, name='edit_group'),               
]
