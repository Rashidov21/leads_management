# Archived API: import_service/urls.py
# Copied before removing API router
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ImportViewSet

router = DefaultRouter()
router.register(r'', ImportViewSet, basename='import')

urlpatterns = [
    path('upload-excel/', ImportViewSet.as_view({'post': 'upload_excel'}), name='upload-excel'),
    path('upload-csv/', ImportViewSet.as_view({'post': 'upload_csv'}), name='upload-csv'),
    path('status/', ImportViewSet.as_view({'get': 'status'}), name='import-status'),
]
