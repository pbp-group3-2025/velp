from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("create/", views.create_report, name="create"),
    path("mod/", views.mod_list, name="mod_list"),
    path("my/", views.my_reports, name="my"),
    path("update/<int:pk>/", views.update_report, name="update"),
    path("update/<int:pk>/status/", views.update_report_status, name="update_status"),
]