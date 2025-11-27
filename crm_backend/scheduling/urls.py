"""URL configuration for scheduling module."""
from django.urls import path
from . import views

app_name = 'scheduling'

urlpatterns = [
    path('groups/', views.groups_list, name='groups_list'),
    path('groups/filter/', views.filter_groups, name='filter_groups'),
    path('rooms/occupancy/', views.room_occupancy_grid, name='room_occupancy'),
    path('courses/', views.courses_list, name='courses_list'),
]
