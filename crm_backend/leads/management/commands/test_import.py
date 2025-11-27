"""Management command to test import functionality."""
from django.core.management.base import BaseCommand
from django.utils import timezone
from import_service.service import ImportProcessor, DuplicateChecker
from leads.models import Lead, ImportLog


class Command(BaseCommand):
    help = 'Test the import functionality with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of test leads to import'
        )
        parser.add_argument(
            '--source',
            type=str,
            default='manual',
            help='Lead source'
        )

    def handle(self, *args, **options):
        count = options['count']
        source = options['source']

        self.stdout.write(f'Importing {count} test leads...')

        # Generate test data
        test_leads = []
        for i in range(1, count + 1):
            test_leads.append({
                'name': f'Test Lead {i}',
                'phone': f'555010{i:04d}'
            })

        # Import leads
        imported_count, duplicate_count, errors = ImportProcessor.import_leads(
            test_leads,
            source=source
        )

        # Create import log
        import_log = ImportLog.objects.create(
            import_type='manual_test',
            status='completed',
            total_records=count,
            imported_count=imported_count,
            duplicate_count=duplicate_count,
            error_count=len(errors),
            error_details={'errors': errors} if errors else {},
            completed_at=timezone.now()
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Successfully imported {imported_count} leads\n'
                f'✓ Duplicates skipped: {duplicate_count}\n'
                f'✓ Errors: {len(errors)}'
            )
        )

        # Display stats
        total_leads = Lead.objects.count()
        new_leads = Lead.objects.filter(status='new').count()

        self.stdout.write(
            f'\nDatabase stats:\n'
            f'Total leads: {total_leads}\n'
            f'New leads: {new_leads}'
        )
