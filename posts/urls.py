from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.post_list, name='list'),
    path('<uuid:pk>/', views.post_detail, name='detail'),
    path('<uuid:pk>/edit/', views.post_update, name='update'),
    path('<uuid:pk>/delete/', views.post_delete, name='delete'),
    path('api/create/', views.api_create, name='api_create'),
    path('api/<uuid:pk>/update/', views.api_post_update, name='api_update'),
    path('api/<uuid:pk>/delete/', views.api_post_delete, name='api_delete'),
    path('api/<uuid:pk>/like-toggle/', views.api_like_toggle, name='api_like_toggle'),
    path('api/<uuid:pk>/comment/', views.api_comment_create, name='api_comment_create'),
    path('api/comment/<uuid:cid>/delete/', views.api_comment_delete, name='api_comment_delete'),
]
