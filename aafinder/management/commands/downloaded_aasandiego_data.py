from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from aafinder.importer.downloader import download_all
from aafinder.importer.utils import get_or_create_downloads_folder


def reset():
    downloads_folder = get_or_create_downloads_folder()
    for path in Path(downloads_folder).iterdir():
        path.unlink()


class Command(BaseCommand):
    help = 'Imports all the downloaded aasandiego html files'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        try:
            count = download_all()
        except Exception as ex:
            import traceback; traceback.print_exc()
            raise CommandError("Could not import stuff. %s" % str(ex))

        self.stdout.write(
            self.style.SUCCESS('Successfully downloaded %s pages.' % count))
