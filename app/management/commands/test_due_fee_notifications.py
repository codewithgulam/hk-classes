# filepath: /c:/Users/gswip.mohdl/Desktop/Laraib/my_prj/home/grouperp/ERP/app/management/commands/test_due_fee_notifications.py
from django.core.management.base import BaseCommand
from app.models import Fee
from datetime import date, timedelta

def get_fees_due_soon():
    today = date.today()
    due_date_threshold = today + timedelta(days=7)
    fees_due_soon = Fee.objects.filter(due_date__lte=due_date_threshold, is_paid=False)
    return fees_due_soon

class Command(BaseCommand):
    help = 'Test the due fee notification feature'

    def handle(self, *args, **kwargs):
        fees_due_soon = get_fees_due_soon()
        if fees_due_soon.exists():
            self.stdout.write(self.style.SUCCESS('Fees due soon:'))
            for fee in fees_due_soon:
                self.stdout.write(f"{fee.student.admin.first_name} {fee.student.admin.last_name} - Due Date: {fee.due_date}")
        else:
            self.stdout.write(self.style.SUCCESS('No fees are due soon.'))