from django.urls import path, include
from report.views import show_main, create_report, show_report, show_xml, show_json, show_xml_by_id, show_json_by_id
from main.views import register
from main.views import login_user, logout_user
from report.views import edit_report
from report.views import delete_report

app_name = 'report'

urlpatterns = [
    path('', show_main, name='main'),
    path('report/create/', create_report, name='create_report'),
    path('report/<str:id>/', show_report, name='show_report'),
    path('xml/', show_xml, name='show_xml'),
    path('json/', show_json, name='show_json'),
    path('xml/<str:id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/<str:id>/', show_json_by_id, name='show_json_by_id'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('report/<str:id>/edit', edit_report, name='edit_report'), # <uuid:id>
    path('report/<str:id>/delete', delete_report, name='delete_report'),
]
