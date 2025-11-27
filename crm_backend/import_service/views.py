"""Simple Django views for import upload and status (non-API)."""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .tasks import manual_import_file
from leads.models import ImportLog


@login_required
def upload_excel(request):
    if request.method == 'POST':
        file_obj = request.FILES.get('file')
        if not file_obj or not file_obj.name.endswith('.xlsx'):
            return render(request, 'import.html', {'error': 'Please upload a valid .xlsx file'})

        import tempfile, os
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, file_obj.name)
        with open(file_path, 'wb') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)

        manual_import_file.delay(file_path=file_path, import_type='excel', user_id=request.user.id)
        return redirect('import_status')

    return render(request, 'import.html')


@login_required
def upload_csv(request):
    if request.method == 'POST':
        file_obj = request.FILES.get('file')
        if not file_obj or not file_obj.name.endswith('.csv'):
            return render(request, 'import.html', {'error': 'Please upload a valid .csv file'})

        import tempfile, os
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, file_obj.name)
        with open(file_path, 'wb') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)

        manual_import_file.delay(file_path=file_path, import_type='csv', user_id=request.user.id)
        return redirect('import_status')

    return render(request, 'import.html')


@login_required
def import_status(request):
    logs = ImportLog.objects.all().order_by('-started_at')[:20]
    return render(request, 'import.html', {'import_logs': logs})
