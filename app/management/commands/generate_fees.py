# filepath: /c:/Users/gswip.mohdl/Desktop/Laraib/my_prj/home/grouperp/ERP/app/management/commands/generate_fees.py
from django.core.management.base import BaseCommand
from app.models import Fee

class Command(BaseCommand):
    help = 'Generate fees for all students'

    def handle(self, *args, **kwargs):
        Fee.generate_fees()
        self.stdout.write(self.style.SUCCESS('Successfully generated fees for all students'))