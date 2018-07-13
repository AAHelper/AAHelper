from collections import defaultdict
from pathlib import Path
from lxml import html
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from .utils import get_or_create_downloads_folder
from .converter import normalize_children
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


def extract_address_and_url(el):
    try:
        anchor = el.xpath("./a")[0]
    except IndexError:
        return '', ''

    url = urlparse(anchor.attrib['href'])
    query = parse_qs(url.query)

    if 'q' not in query:
        return '', anchor.attrib['href']

    return query['q'][0], anchor.attrib['href']


class Parser:
    downloads_dir = get_or_create_downloads_folder()
    name = None
    code_map = {c.code: c for c in MeetingCode.objects.all()}

    def parse_all(self):
        count = 0
        for path in Path(self.downloads_dir).iterdir():
            if path.name != 'legend.html':
                self.name = path.name.split(".")[0]
                if self.name[-1].isnumeric():
                    self.name = self.name[:-1]
                print(path)
                data = self.parse(path)
                # import ipdb; ipdb.set_trace()
                count += self.insert_data(data)
        return count

    def parse(self, path):
        print(f"\n\n\nParsing file {path}\n\n")
        dom = html.document_fromstring(path.read_text())
        normalize_children(dom)
        # print(html.tostring(dom))
        rows = dom.xpath('//table[@width="90%"]/tr[not(self::td)]')
        if any([r.xpath("./td/strong") for r in rows]):
            return self.parse_with_days(rows)
        return self.parse_without_days(rows)

    def _parse_inner(self, tds):
        time = get_flattened_text(tds[0]).strip()
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

        name = tds[1].text.strip()
        if name is None:
            import ipdb; ipdb.set_trace()

        street_address, url = extract_address_and_url(tds[1])
        street_address = street_address.strip()

        code = get_flattened_text(tds[2]).strip()
        codes = code.split()
        # for code in code.split():
        #     if code in SPECIAL_CODES:
        #         codes.append(SPECIAL_CODES[code])
        # code = ", ".join(codes)
        area = get_flattened_text(tds[3]).strip()

        return time, name, street_address, url, code, codes, area

    def parse_with_days(self, rows):
        day_map = defaultdict(list)
        for i, tr in enumerate(rows[1:]):
            # print("*" * 100)
            # print(i, html.tostring(tr))

            tds = tr.xpath("./td")

            try:
                location_type = tds[1].xpath("./br")[0].tail.strip()
            except IndexError:
                this_day = tds[1].xpath("./strong")
                if this_day:
                    day = this_day[0].text
                    continue

            time, name, street_address, url, code, codes, area = self._parse_inner(tds)
            day_map[day].append({
                "time": time,
                "name": name,
                "street_address": street_address,
                "location_type": location_type,
                "codes": codes,
                "area": area,
                "url": url,
            })

        # pprint(day_map)
        # print("*" * 100)
        return day_map

    def parse_without_days(self, rows):
        locations = []
        for i, tr in enumerate(rows[1:]):
            # print("*" * 100)
            # print(i, html.tostring(tr))

            tds = tr.xpath("./td")
            try:
                location_type = tds[1].xpath("./br")[0].tail.strip()
            except IndexError:
                location_type = ""

            time, name, street_address, url, code, codes, area = self._parse_inner(tds)

            locations.append({
                "time": time,
                "name": name,
                "street_address": street_address,
                "location_type": location_type,
                "codes": codes,
                "area": area,
                "url": url,
            })

        # pprint(locations)
        # print("*" * 100)
        return locations

    def insert_data(self, data):
        count = 0
        if isinstance(data, dict):
            return self.insert_dict_data(data)

        for item in data:
            count += self.insert_list_data(item)
        print(len(data), count)
        return count

    def insert_dict_data(self, data):
        count = 0
        total_items = 0
        for day, items in data.items():
            total_items += len(items)
            for item in items:
                count += self.insert_list_data(item, day_of_week=day)

        print(total_items, count)
        return count

    def insert_list_data(self, item, day_of_week=None):
        count = 0
        with transaction.atomic():
            location, created = Location.objects.get_or_create(
                address_string=item['street_address'])
            area, created = MeetingArea.objects.get_or_create(area=item['area'])
            meeting, created = Meeting.objects.get_or_create(
                name=item['name'], location=location, time=item['time'],
                defaults={
                    'url': item['url'],
                    'area': area,
                }
            )
            if created:
                count = 1
            # else:
            #     import ipdb; ipdb.set_trace()
            if item['codes']:
                for code in item['codes']:
                    if code in self.code_map:
                        meeting.codes.add(self.code_map[code])
            if day_of_week:
                mt, created = MeetingType.objects.get_or_create(
                    type=day_of_week)
                meeting.types.add(mt)
            else:
                mt, created = MeetingType.objects.get_or_create(
                    type=self.name)
                meeting.types.add(mt)

        return count