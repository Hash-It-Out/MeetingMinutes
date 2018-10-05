from django.contrib import admin

# Register your models here.
from .models import Team, Meeting, MeetingAttendee, Decision

admin.site.register(Team)
admin.site.register(Meeting)
admin.site.register(MeetingAttendee)
admin.site.register(Decision)