from django.urls import path, include
from booking.views import show_main, create_booking, show_booking, show_xml, show_json, show_xml_by_id, show_json_by_id
from main.views import register
from main.views import login_user, logout_user
from booking.views import edit_booking
from booking.views import delete_booking

app_name = 'booking'

urlpatterns = [
    path('', show_main, name='main'),
    path('booking/create/', create_booking, name='create_booking'),
    path('booking/<str:id>/', show_booking, name='show_booking'),
    path('xml/', show_xml, name='show_xml'),
    path('json/', show_json, name='show_json'),
    path('xml/<str:id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/<str:id>/', show_json_by_id, name='show_json_by_id'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('booking/<str:id>/edit', edit_booking, name='edit_booking'), # <uuid:id>
    path('booking/<str:id>/delete', delete_booking, name='delete_booking'),
]
