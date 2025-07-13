from django.core.management.base import BaseCommand
from rewards.models import Reward
from core.models import User

class Command(BaseCommand):
    help = 'Populates the database with initial rewards for the shop.'

    def handle(self, *args, **options):
        self.stdout.write('Deleting existing rewards...')
        Reward.objects.all().delete()
        
        # Get the first user to be the creator of the rewards
        creator = User.objects.first()
        if not creator:
            self.stdout.write(self.style.ERROR('No users found. Please create a user first.'))
            return
            
        rewards = [
            {'title': 'یک فنجان قهوه', 'description': 'یک فنجان قهوه یا چای در کافه', 'cost': 50},
            {'title': 'بلیط سینما', 'description': 'یک بلیط سینما برای فیلم دلخواه', 'cost': 100},
            {'title': 'یک شاخه گل', 'description': 'یک شاخه گل رز زیبا', 'cost': 30},
            {'title': 'ماساژ', 'description': 'یک جلسه ماساژ آرامش‌بخش', 'cost': 150},
            {'title': 'کتاب', 'description': 'یک کتاب از نویسنده مورد علاقه', 'cost': 80},
        ]
        
        self.stdout.write('Creating initial rewards...')
        for reward_data in rewards:
            Reward.objects.create(creator=creator, recipient=creator, **reward_data)
            
        self.stdout.write(self.style.SUCCESS('Successfully populated the database with initial rewards.'))
