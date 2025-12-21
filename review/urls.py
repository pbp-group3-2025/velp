from django.urls import path
from . import views

app_name = "review"

urlpatterns = [
    path('add/<uuid:venue_id>/', views.add_review, name='add_review'),
    path('add/', views.add_review_general, name='add_review_general'), 
    path('delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('edit/<int:review_id>/', views.edit_review, name='edit_review'),
    path('add_review_ajax/<uuid:venue_id>/', views.add_review_with_ajax, name='add_review_with_ajax'),
    path('edit_review_ajax/<int:review_id>/', views.edit_review_ajax, name='edit_review_ajax'),
    path('venue/<uuid:venue_id>/json/', views.get_reviews_by_venue_json, name='get_reviews_json'),
    path('add_review_ajax/<uuid:venue_id>/', views.add_review_ajax_flutter, name='add_review_ajax_flutter'),
    path('edit_review_ajax/<int:review_id>/', views.edit_review_ajax_flutter, name='edit_review_ajax_flutter'),
    path('delete_review/<int:review_id>/', views.delete_review_flutter, name='delete_review_flutter'),

]