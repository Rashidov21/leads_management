# Archived API: import_service/views.py
# Copied before removing API viewset

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .tasks import manual_import_file
from leads.models import ImportLog


class ImportViewSet(viewsets.ViewSet):
    """ViewSet for handling file imports."""
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    @action(detail=False, methods=['post'])
    def upload_excel(self, request):
        """Upload and import Excel file."""
        file_obj = request.FILES.get('file')
        
        if not file_obj:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not file_obj.name.endswith('.xlsx'):
            return Response(
                {'error': 'Only .xlsx files are supported'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save file temporarily
        import tempfile
        import os
        
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, file_obj.name)
        
        with open(file_path, 'wb') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)
        
        # Start import task
        manual_import_file.delay(
            file_path=file_path,
            import_type='excel',
            user_id=request.user.id
        )
        
        return Response({
            'status': 'File uploaded and import started',
            'file_name': file_obj.name
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=['post'])
    def upload_csv(self, request):
        """Upload and import CSV file."""
        file_obj = request.FILES.get('file')
        
        if not file_obj:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not file_obj.name.endswith('.csv'):
            return Response(
                {'error': 'Only .csv files are supported'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save file temporarily
        import tempfile
        import os
        
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, file_obj.name)
        
        with open(file_path, 'wb') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)
        
        # Start import task
        manual_import_file.delay(
            file_path=file_path,
            import_type='csv',
            user_id=request.user.id
        )
        
        return Response({
            'status': 'File uploaded and import started',
            'file_name': file_obj.name
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get import status."""
        logs = ImportLog.objects.all().order_by('-started_at')[:10]
        
        data = []
        for log in logs:
            data.append({
                'id': log.id,
                'import_type': log.get_import_type_display(),
                'status': log.get_status_display(),
                'total_records': log.total_records,
                'imported_count': log.imported_count,
                'duplicate_count': log.duplicate_count,
                'error_count': log.error_count,
                'started_at': log.started_at.isoformat(),
                'completed_at': log.completed_at.isoformat() if log.completed_at else None,
            })
        
        return Response(data)
