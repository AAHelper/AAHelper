import requests
from django.db import models
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.utils.text import slugify


class Location(models.Model):
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=5)
    address_string = models.CharField(max_length=500)
    location = models.PointField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.location is None:
            params={
                "address": self.address_string,
                "key":"AIzaSyCRB2jA_b4InjlQtslR5g5NO9n8dUTdJ0Q"
            }
            resp = requests.get("https://maps.googleapis.com/maps/api/geocode/json", params=params)
            if resp.ok:
                try:
                    j = resp.json()
                    loc = j['results'][0]['geometry']['location']
                    y = loc['lat']
                    x = loc['lng']
                    p = Point(x=x, y=y)
                    self.location = p
                except:
                    pass
        super().save(*args, **kwargs)

    def __str__(self):
        return self.address_string


class MeetingCode(models.Model):
    code = models.CharField(max_length=5)
    description = models.CharField(max_length=100)
    # slug = models.SlugField()

    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         self.slug = slugify(self.code)
    #     super().save(*args, **kwargs)

    def __str__(self):
        return self.description


class MeetingType(models.Model):
    type = models.CharField(max_length=50)
    slug = models.SlugField()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.type)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.type


class MeetingArea(models.Model):
    area = models.CharField(max_length=100)
    slug = models.SlugField()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.area)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.area


class Meeting(models.Model):
    name = models.CharField(max_length=200)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    time = models.TimeField(auto_now=False, auto_now_add=False, db_index=True)
    url = models.URLField(max_length=500)
    area = models.ForeignKey(
        MeetingArea, on_delete=models.CASCADE, blank=True, null=True)
    codes = models.ManyToManyField(MeetingCode) #, through='CodeMap')
    types = models.ManyToManyField(MeetingType) #, through='TypeMap')
    row_src = models.TextField(blank=True)
    orig_filename = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name


#class CodeMap(models.Model):
#    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
#    meetingcode = models.ForeignKey(MeetingCode, on_delete=models.CASCADE)
#
#    class Meta:
#        db_table = 'aafinder_meeting_codes'


#class TypeMap(models.Model):
#    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
#    meetingtype = models.ForeignKey(MeetingType, on_delete=models.CASCADE)
#
#    class Meta:
#        db_table = 'aafinder_meeting_types'
