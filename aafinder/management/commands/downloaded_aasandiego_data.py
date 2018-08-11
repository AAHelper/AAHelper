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

    def add_arguments(self, parser):
        parser.add_argument('--force_save', dest='force_save', action='store_true')

    def handle(self, *args, **options):
        force_save = options['force_save']
        try:
            count = download_all(force_save=force_save)
        except Exception as ex:
            import traceback; traceback.print_exc()
            raise CommandError("Could not import stuff. %s" % str(ex))

        self.stdout.write(
            self.style.SUCCESS('Successfully downloaded %s pages.' % count))
