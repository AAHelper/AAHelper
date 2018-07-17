from django.contrib import admin
from aafinder.models import Location, MeetingCode, MeetingType, Meeting, MeetingArea

class MeetingAdmin(admin.ModelAdmin):
    list_display = ('name', 'time', 'area',)
    list_filter = ('types', 'time')
    search_fields = ('name', )

admin.site.register(Location)
admin.site.register(MeetingCode)
admin.site.register(MeetingType)
admin.site.register(MeetingArea)
admin.site.register(Meeting, MeetingAdmin)
