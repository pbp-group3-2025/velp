from django.urls import path
from . import views

urlpatterns = [
    path('<int:venue_id>/add/', views.add_review, name='add_review'),
]