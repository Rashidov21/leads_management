"""URL configuration for trials module."""
from django.urls import path
from . import views

app_name = 'trials'

urlpatterns = [
    path('', views.trials_list, name='trials_list'),
    path('schedule/', views.schedule_trial, name='schedule_trial'),
    path('<int:pk>/mark_attended/', views.mark_attended, name='mark_attended'),
    path('<int:pk>/mark_no_show/', views.mark_no_show, name='mark_no_show'),
    path('<int:pk>/make_offer/', views.make_sales_offer, name='make_offer'),
]
