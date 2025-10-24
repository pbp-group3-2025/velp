from django.urls import path, include
from main.views import show_main, create_venue, show_venue, show_xml, show_json, show_xml_by_id, show_json_by_id
from main.views import register
from main.views import login_user, logout_user
from main.views import edit_venue
from main.views import delete_venue


app_name = 'main'


urlpatterns = [
    path('', show_main, name='show_main'),
    path('venue/create/', create_venue, name='create_venue'),
    path('venue/<str:id>/', show_venue, name='show_venue'),
    path('xml/', show_xml, name='show_xml'),
    path('json/', show_json, name='show_json'),
    path('xml/<str:id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/<str:id>/', show_json_by_id, name='show_json_by_id'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('venue/<str:id>/edit', edit_venue, name='edit_venue'), # <uuid:id>
    path('news/<str:id>/delete', delete_venue, name='delete_venue'),
]

