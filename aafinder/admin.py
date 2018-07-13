from django.contrib import admin
from aafinder.models import Location, MeetingCode, MeetingType, Meeting

class MeetingAdmin(admin.ModelAdmin):
    list_display = ('name', 'time', 'area',)
    list_filter = ('types', 'time')

admin.site.register(Location)
admin.site.register(MeetingCode)
admin.site.register(MeetingType)
admin.site.register(Meeting, MeetingAdmin)
