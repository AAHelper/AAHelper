from django.urls import reverse
from django.utils.html import escapejs
from django.template import defaultfilters
from django import template
import datetime
import functools

CACHE = {}

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    chks = []
    key = ",".join(l)
    if key not in CACHE:
        for i in range(0, len(l), n):
            chks.append(l[i:i + n])
        CACHE[key] = chks
    return CACHE[key]

register = template.Library()
@register.inclusion_tag('aasandiego/inclusion_tags/map_js.html', takes_context=True)
def render_map_js(context):
    latest_meeting_list = context['latest_meeting_list']
    locations = {}
    meetings = []

    # gather up all the meeting locations
    for meeting in latest_meeting_list:
        if meeting.location not in locations:
            locations[meeting.location] = []
            locations[meeting.location].append(meeting)

        mtime = meeting.time.strftime("%I:%M %p")
        meeting_types = sorted([m.type for m in meeting.types.all().order_by('type')])
        meeting_chunks = chunks(meeting_types, 3)
        days = "<br />".join(", ".join(chunk) for chunk in meeting_chunks)
        locations[meeting.location].append(
            f'<p>{meeting.name}<br />{days} <br />{mtime}</p><hr />'
        )

    # append the location to the end of the meeting locations.
    for location, locations in locations.items():
        meeting = locations.pop(0)
        url = reverse('aafinder:meetings_by_location', kwargs={'pk': meeting.location_id} )
        locations.append(
            f'<p><a href="{url}">Other Meetings at this location.</a></p>'
        )
        locations = " ".join(locations)
        locations = locations.replace("'", "\\'")
        x = location.location.x if location.location else None
        y = location.location.y if location.location else None
        meetings.append({'meeting': meeting, 'location': locations, 'x': x, 'y': y})
        meeting.name = meeting.name.replace("\n", "")
    
    return {
        'meetings': meetings,
        'locations': locations
    }
