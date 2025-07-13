from django.core.management.base import BaseCommand
from rewards.models import RewardCategory

class Command(BaseCommand):
    help = 'ایجاد دسته‌بندی‌های پیش‌فرض جوایز'

    def handle(self, *args, **options):
        categories = [
            {'name': 'شب قرار عاشقانه', 'icon': 'bi-heart'},
            {'name': 'ماساژ', 'icon': 'bi-hand-index-thumb'},
            {'name': 'هدیه', 'icon': 'bi-gift'},
            {'name': 'غذا', 'icon': 'bi-cup-hot'},
            {'name': 'لطف ویژه', 'icon': 'bi-stars'},
            {'name': 'شب فیلم', 'icon': 'bi-film'},
            {'name': 'فعالیت', 'icon': 'bi-bicycle'},
            {'name': 'سایر موارد', 'icon': 'bi-three-dots'},
        ]
        
        created_count = 0
        for category in categories:
            _, created = RewardCategory.objects.get_or_create(
                name=category['name'],
                defaults={'icon': category['icon']}
            )
            if created:
                created_count += 1
                self.stdout.write(f"دسته‌بندی ایجاد شد: {category['name']}")
        
        self.stdout.write(self.style.SUCCESS(f'{created_count} دسته‌بندی جدید ایجاد شد')) 