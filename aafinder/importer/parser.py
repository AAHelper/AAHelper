import re
from operator import itemgetter
from pathlib import Path
from lxml import html
from lxml.html.clean import Cleaner
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from .utils import get_or_create_downloads_folder
from aafinder.models import (
    MeetingType, Location,
    Meeting, MeetingCode, MeetingArea
)
from django.db import transaction


def get_flattened_text(el):
    """
    Returns the text contents of an element.
    """
    els = list(el.iter())
    out = []
    for e in els:
        if e.text is not None:
            out.append(e.text)
        if e.tail is not None:
            out.append(e.tail)

    return ''.join(out)


class Parser:
    downloads_dir = get_or_create_downloads_folder()
    name = None
    code_map = {c.code: c for c in MeetingCode.objects.all()}
    tds = None
    day = None
    c_filename = None
    time_td = itemgetter(0)
    meeting_name_td = itemgetter(1)
    location_td = itemgetter(1)
    anchor_td = itemgetter(1)
    codes_td = itemgetter(2)
    days_td = itemgetter(2)
    area_td = itemgetter(3)
    meeting_areas = {}
    meeting_types = {}
    cleaner = Cleaner(
        remove_tags=["p", "span", "font"], kill_tags=['script', 'style'])
    group_days = {
        'Daily': [
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
            "Saturday", "Sunday"],
        'Mo-Su': [
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
            "Saturday", "Sunday"],
        'Mo-Sa': [
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
            "Saturday"],
        'Mo-Sat': [
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
            "Saturday"],
        'Mo-Fr': ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        'Sat-Sun': ["Saturday", "Sunday"],
        'Mo': ['Monday'],
        'Tu': ['Tuesday'],
        'We': ['Wednesday'],
        'Th': ['Thursday'],
        'Fr': ['Friday'],
        'Sa': ['Saturday'],
        'Su': ['Sunday'],
        'Monday': ['Monday'],
        'Tuesday': ['Tuesday'],
        'Wednesday': ['Wednesday'],
        'Thursday': ['Thursday'],
        'Friday': ['Friday'],
        'Saturday': ['Saturday'],
        'Sunday': ['Sunday'],
    }
    group_days['Mo-Sun'] = group_days['Mo-Su']
    day_re = re.compile(r'([\w]+-[\w]+)')
    weekday_re = re.compile(
        r'([Mo]{2}|[Tu]{2}|[We]{2}|[Th]{2}|[Fr]{2}|[Sa]{2}|[Su]{2})')

    @property
    def time(self):
        time = get_flattened_text(self.time_td(self.tds)).strip()

        if "::" in time:
            time = time.replace("::", ":")
        if time.endswith("N"):
            time = "12:00"
        if time[-1] in ['A', 'P']:
            time = time + "M"

        try:
            in_time = datetime.strptime(time, "%I:%M%p")
            time = datetime.strftime(in_time, "%H:%M")
        except ValueError:
            if len(time) == 5:
                # it's noon
                pass
            else:
                raise
        return time

    @property
    def meeting_name(self):
        name = self.meeting_name_td(self.tds).text.strip()
        if name is None:
            import ipdb; ipdb.set_trace()
        return name

    def _extract_anchor(self, el):
        try:
            anchor = el.xpath("./a")[0]
        except IndexError:
            return ''

        return anchor

    @property
    def street_address(self):
        anchor = self._extract_anchor(self.anchor_td(self.tds))

        if anchor != '':

            try:
                url = urlparse(anchor.attrib['href'])
            except Exception as ex:
                import ipdb; ipdb.set_trace()

            query = parse_qs(url.query)

            if 'q' not in query:
                return ''

            return query['q'][0].strip()

        return ''

    @property
    def url(self):
        anchor = self._extract_anchor(self.anchor_td(self.tds))
        if anchor != '':
            return anchor.attrib['href']
        return ''

    @property
    def codes(self):
        codes = get_flattened_text(self.codes_td(self.tds)).strip().split()
        return codes

    @property
    def area(self):
        area = get_flattened_text(self.area_td(self.tds)).strip()
        area = ' '.join(area.split())

        if area.startswith("* "):
            import ipdb; ipdb.set_trace()
        return area

    @property
    def location_type(self):
        try:
            location_type = self.location_td(self.tds).xpath("./br")[0].tail.strip()
        except IndexError:
            return ''

        return location_type

    @property
    def days(self):
        day_td = self.days_td(self.tds)
        # GAH, I hate Regexes, but Whatever
        td_text = day_td.text.strip()
        matches = self.day_re.match(td_text)
        active_days = []
        if matches:
            for group in matches.groups():
                if group in self.group_days:
                    active_days.extend(self.group_days[group])

            return active_days

        if "," in day_td.text:
            matches = self.weekday_re.findall(td_text)
            if matches:
                for match in matches:
                    if match in self.group_days:
                        active_days.extend(self.group_days[match])
                return active_days

        if 'Daily' in td_text and 'Sunday' in td_text:
            for day in self.group_days['Daily']:
                if day != 'Sunday':
                    active_days.append(day)
            return active_days

        if self.day in self.group_days:
            return self.group_days[self.day]

        if self.name in self.group_days:
            return self.group_days[self.name]

        if self.day:
            return [self.day]

        return [self.name]

    @property
    def notes(self):
        tr = self.tr
        # print(self.meeting_name, self.location_type)
        # print(html.tostring(tr).strip())

        notes = self.get_flattened_text(tr)
        if self.time_td(tr).text:
            notes = notes.replace(self.time_td(tr).text, '')
        if self.meeting_name_td(tr).text:
            notes = notes.replace(self.meeting_name_td(tr).text, '').strip()
        if self.location_td(tr).text:
            notes = notes.replace(self.location_td(tr).text, '').strip()
        if self.anchor_td(tr).text:
            try:
                notes = notes.replace(
                    self.anchor_td(tr).xpath("./a")[0].text.strip(), '')
            except Exception as ex:
                del ex
                pass
            notes = notes.replace(self.anchor_td(tr).text, '').strip()
        if self.codes_td(tr).text:
            notes = notes.replace(self.codes_td(tr).text, '').strip()
        if self.area_td(tr).text:
            notes = notes.replace(self.area_td(tr).text, '').strip()
        if self.days_td(tr).text:
            notes = notes.replace(self.days_td(tr).text, '').strip()
        notes = " ".join(notes.replace("\n", ' ').split())
        # print(f"Note: {notes}.\n")
        return notes

    def parse_all(self):
        count = 0
        for path in Path(self.downloads_dir).iterdir():
            if path.is_dir():
                continue
            self.day = None
            if path.name != 'legend.html':
                self.name = path.name.split(".")[0]
                if self.name[-1].isnumeric():
                    self.name = self.name[:-1]
                data = self.parse(path)
                count += self.insert_data(data)
        return count

    def set_default_itemgetters(self):
        self.time_td = itemgetter(0)
        self.meeting_name_td = itemgetter(1)
        self.location_td = itemgetter(1)
        self.anchor_td = itemgetter(1)
        self.codes_td = itemgetter(2)
        self.days_td = itemgetter(2)
        self.area_td = itemgetter(3)

    def set_meeting_itemgetters(self):
        self.time_td = itemgetter(0)
        self.meeting_name_td = itemgetter(1)
        self.location_td = itemgetter(1)
        self.anchor_td = itemgetter(1)
        self.codes_td = itemgetter(3)
        self.area_td = itemgetter(4)

    def parse(self, path):
        print(f"Parsing file {path}")
        self.c_filename = path
        dom = html.document_fromstring(path.read_text())

        dom = self.cleaner.clean_html(dom)
        rows = dom.xpath('//table[@width="90%"]/tr[not(self::td)]')

        self.set_default_itemgetters()

        if 'Meetings' in self.name:
            self.set_meeting_itemgetters()

        return self._parse(rows)

    def get_flattened_text(self, el):
        """
        Returns the text contents of an element.
        """
        els = list(el.iter())
        out = []
        for e in els:
            if e.text is not None:
                out.append(e.text)
            if e.tail is not None:
                out.append(e.tail)

        return ''.join(out)

    def _parse(self, rows):
        locations = []
        for i, tr in enumerate(rows[1:]):

            self.tr = tr

            self.tds = tr.xpath("./td")
            if self.check_and_set_day():
                continue

            locations.append({
                "time": self.time,
                "name": self.meeting_name,
                "street_address": self.street_address,
                "location_type": self.location_type,
                "notes": self.notes,
                "codes": self.codes,
                "area": self.area,
                "url": self.url,
                "days": self.days,
                "row": html.tostring(tr),
                "orig_file": self.c_filename,
            })

        return locations

    def check_and_set_day(self):
        this_day = self.tds[1].xpath("./strong")
        if this_day:
            self.day = this_day[0].text.strip()
            return True
        return False

    def insert_data(self, data):
        count = 0

        for item in data:
            count += self.insert_list_data(item)
        print("Imported {0} of {1} items".format(count, len(data)))
        return count

    def insert_list_data(self, item, day_of_week=None):
        count = 0
        with transaction.atomic():
            location, created = Location.objects.get_or_create(
                address_string=item['street_address'])
            if item['area'] not in self.meeting_areas:
                area, created = MeetingArea.objects.get_or_create(
                    area=item['area'])
                self.meeting_areas.update({item['area']: area})
            else:
                area = self.meeting_areas[item['area']]

            meeting, created = Meeting.objects.get_or_create(
                name=item['name'], location=location, time=item['time'],
                defaults={
                    'url': item['url'],
                    'area': area,
                    'row_src': item['row'],
                    'orig_filename': item['orig_file'],
                    'notes': item['notes']
                }
            )
            if created:
                count = 1

            if item['codes']:
                for code in item['codes']:
                    if code in self.code_map:
                        meeting.codes.add(self.code_map[code])

            for day in item['days']:
                day = day.strip()
                if day not in self.meeting_types:
                    mt, created = MeetingType.objects.get_or_create(
                        type=day.strip())
                    self.meeting_types.update({day: mt})
                else:
                    mt = self.meeting_types[day]

                meeting.types.add(mt)

        return count