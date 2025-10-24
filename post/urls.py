from django.urls import path, include
from post.views import show_main, create_post, show_post, show_xml, show_json, show_xml_by_id, show_json_by_id
from main.views import register
from main.views import login_user, logout_user
from post.views import edit_post
from post.views import delete_post

app_name = 'post'

urlpatterns = [
    path('', show_main, name='main'),
    path('post/create/', create_post, name='create_post'),
    path('post/<str:id>/', show_post, name='show_post'),
    path('xml/', show_xml, name='show_xml'),
    path('json/', show_json, name='show_json'),
    path('xml/<str:id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/<str:id>/', show_json_by_id, name='show_json_by_id'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('post/<str:id>/edit', edit_post, name='edit_post'), # <uuid:id>
    path('post/<str:id>/delete', delete_post, name='delete_post'),
]
