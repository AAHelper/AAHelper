from django.db import models


class Location(models.Model):
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=5)
    address_string = models.CharField(max_length=500)

    def __str__(self):
        return self.address_string


class MeetingCode(models.Model):
    code = models.CharField(max_length=5)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.description


class MeetingType(models.Model):
    type = models.CharField(max_length=50)
    is_day_of_week = models.BooleanField(default=False)

    def __str__(self):
        return self.type


class MeetingArea(models.Model):
    area = models.CharField(max_length=100)

    def __str__(self):
        return self.area


class Meeting(models.Model):
    name = models.CharField(max_length=200)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    time = models.TimeField(auto_now=False, auto_now_add=False, db_index=True)
    url = models.URLField(max_length=500)
    area = models.ForeignKey(
        MeetingArea, on_delete=models.CASCADE, blank=True, null=True)
    codes = models.ManyToManyField(MeetingCode)
    types = models.ManyToManyField(MeetingType)

    def __str__(self):
        return self.name
