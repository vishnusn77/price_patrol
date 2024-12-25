from django.core.management.base import BaseCommand
from tracker.models import APIUsage

class Command(BaseCommand):
    help = "Reset API usage count"

    def handle(self, *args, **kwargs):
        APIUsage.reset_if_needed()
        self.stdout.write("API usage count reset.")
