from django.core.management import BaseCommand
from accounts.models import OtpCode
import datetime
from django.utils import timezone


class Command(BaseCommand):  # this command clears expired otp codes from database
    help = 'this command removes expired otp codes'

    def handle(self, *args, **options):
        expired_time = timezone.now()- datetime.timedelta(minutes=2)
        OtpCode.objects.filter(created_at__lt=expired_time).delete()
        self.stdout.write('all expired otp codes has been removed')
