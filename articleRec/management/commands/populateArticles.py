from django.core.management import BaseCommand


class Command(BaseCommand):

  def handle(self, *args, **options):

    self.stdout("Started the cron job")
