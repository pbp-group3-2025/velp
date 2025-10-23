from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("report/create/", views.create_report, name="create"),
    path("report/mod/", views.mod_list, name="mod_list"),
    path("report/my/", views.my_reports, name="my"),
    path("report/update/<int:pk>/", views.update_report, name="update"),
    path("report/update/<int:pk>/status/", views.update_report_status, name="update_status"),
]