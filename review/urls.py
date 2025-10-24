from django.urls import path, include
from review.views import show_main, create_review, show_review, show_xml, show_json, show_xml_by_id, show_json_by_id
from main.views import register
from main.views import login_user, logout_user
from review.views import edit_review
from review.views import delete_review

app_name = 'review'

urlpatterns = [
    path('', show_main, name='main'),
    path('review/create/', create_review, name='create_review'),
    path('review/<str:id>/', show_review, name='show_review'),
    path('xml/', show_xml, name='show_xml'),
    path('json/', show_json, name='show_json'),
    path('xml/<str:id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/<str:id>/', show_json_by_id, name='show_json_by_id'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('review/<str:id>/edit', edit_review, name='edit_review'), # <uuid:id>
    path('review/<str:id>/delete', delete_review, name='delete_review'),
]
