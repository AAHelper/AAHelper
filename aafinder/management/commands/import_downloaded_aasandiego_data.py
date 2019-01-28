from django.core.management.base import BaseCommand, CommandError
from aafinder.importer.parser import Parser
from aafinder.models import (
    MeetingCode, MeetingType, MeetingArea, Meeting, Location)


def insert_default_meeting_codes():
    meeting_codes = {
        'C': 'CLOSED for Alcoholics & for those "with a desire to stop drinking."',  # noqa: E501
        'M': 'For Men Only',
        'W': 'For Women Only',
        'LGBT': 'Lesbian / Gay / Transgender / Bisexual',
        'BS': 'Babysitting Available',
        '*': 'Wheel Chair Access',
        '+': 'Signed for Hearing Impaired',
        'CF': 'Child Friendly',
    }
    for code, description in meeting_codes.items():
        MeetingCode.objects.get_or_create(code=code, description=description)


def reset():
    MeetingType.objects.all().delete()
    Meeting.objects.all().delete()
    MeetingArea.objects.all().delete()


class Command(BaseCommand):
    help = 'Imports all the downloaded aasandiego html files'


    def handle(self, *args, **options):
        """Import all the downloaded aasandiego.com html files"""
        # Do not reset the database.
        # This was done initially when developing, it's no longer
        # necessary.
        # reset()
        insert_default_meeting_codes()

        p = Parser()
        count = 0
        try:
            count = p.parse_all()
        except Exception as ex:
            import traceback; traceback.print_exc()
            raise CommandError("Could not import stuff. %s" % str(ex))

        self.stdout.write(
            self.style.SUCCESS('Successfully imported %s meetings.' % count))
