from django.core.management import BaseCommand


class Command(BaseCommand):

  def handle(self, *args, **options):

    print("Started the cron job")
