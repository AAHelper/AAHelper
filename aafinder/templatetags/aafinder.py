from django.urls import reverse
from django.utils.html import escapejs
from django.template import defaultfilters
from django import template
import datetime

# defaultfilters.time

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
        days = ",".join(m.type for m in meeting.types.all())
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
    
    return {
        'meetings': meetings,
        'locations': locations
    }
