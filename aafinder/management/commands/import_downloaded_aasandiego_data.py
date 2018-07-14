from django.core.management.base import BaseCommand, CommandError
from aafinder.importer.parser import Parser
from aafinder.models import (
    MeetingCode, MeetingType, MeetingArea, Meeting, Location)


def insert_default_meeting_codes():
    meeting_codes = {
        'C': 'CLOSED for Alcoholics & for those "with a desire to stop drinking."',  # noqa: E501
        'M': 'for Men Only',
        'W': 'for Women Only',
        'LGBT': 'Lesbian/Gay/Transgender/Bisexual',
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
    Location.objects.all().delete()
    insert_default_meeting_codes()


class Command(BaseCommand):
    help = 'Imports all the downloaded aasandiego html files'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        reset()
        p = Parser()
        count = 0
        try:
            count = p.parse_all()
        except Exception as ex:
            import traceback; traceback.print_exc()
            raise CommandError("Could not import stuff. %s" % str(ex))

        self.stdout.write(
            self.style.SUCCESS('Successfully imported %s meetings.' % count))
