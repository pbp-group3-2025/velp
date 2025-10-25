from django.urls import path
from reports.views import create_report, mod_list, my_reports, update_report, update_report_status, delete_report, my_reports
app_name = "reports"

urlpatterns = [
    path("create/", create_report, name="create"),
    path("mod/", mod_list, name="mod_list"),
    path("my/", my_reports, name="my"),
    path("update/<int:pk>/", update_report, name="update"),
    path("update/<int:pk>/status/", update_report_status, name="update_status"),
    path('delete/<int:id>/', delete_report, name='delete'),
    path('my/', my_reports, name='my_reports'),
]