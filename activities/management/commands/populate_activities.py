from django.core.management.base import BaseCommand
from activities.models import Activity

class Command(BaseCommand):
    help = 'Populates the database with initial activities.'

    def handle(self, *args, **options):
        self.stdout.write('Deleting existing activities...')
        Activity.objects.all().delete()
        
        activities = [
            {'title': 'قرار عاشقانه', 'description': 'یک شب را بیرون از خانه با هم بگذرانید.', 'points': 50},
            {'title': 'پختن شام', 'description': 'یک وعده غذایی خوشمزه برای همسرتان بپزید.', 'points': 30},
            {'title': 'تماشای فیلم', 'description': 'یک فیلم عاشقانه با هم تماشا کنید.', 'points': 20},
            {'title': 'پیاده‌روی', 'description': 'یک پیاده‌روی طولانی در پارک داشته باشید.', 'points': 15},
            {'title': 'نوشتن نامه عاشقانه', 'description': 'یک نامه عاشقانه برای همسرتان بنویسید.', 'points': 40},
        ]
        
        self.stdout.write('Creating initial activities...')
        for activity_data in activities:
            Activity.objects.create(**activity_data)
            
        self.stdout.write(self.style.SUCCESS('Successfully populated the database with initial activities.'))
