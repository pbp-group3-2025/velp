from django.urls import path, include
from community.views import show_main, create_community, show_community, show_xml, show_json, show_xml_by_id, show_json_by_id
from main.views import register
from main.views import login_user, logout_user
from community.views import edit_community
from community.views import delete_community

app_name = 'community'

urlpatterns = [
    path('', show_main, name='main'),
    path('community/create/', create_community, name='create_community'),
    path('community/<str:id>/', show_community, name='show_community'),
    path('xml/', show_xml, name='show_xml'),
    path('json/', show_json, name='show_json'),
    path('xml/<str:id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/<str:id>/', show_json_by_id, name='show_json_by_id'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('community/<str:id>/edit', edit_community, name='edit_community'), # <uuid:id>
    path('community/<str:id>/delete', delete_community, name='delete_community'),
]
