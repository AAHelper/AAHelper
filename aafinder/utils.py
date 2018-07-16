import datetime


def get_now_and_offset(default_offset=3):
    now = datetime.datetime.now()

    # now = now - datetime.timedelta(hours=1)

    hours_from_now = now + datetime.timedelta(hours=3)

    return now, hours_from_now


def now():
    return round_to_nearset_minute(datetime.datetime.now())


def get_date_offset(default_offset=3):
    return round_to_nearset_minute(now() + datetime.timedelta(hours=default_offset))


def get_now_date():
    return now()


def get_now_time():
    return now().time()


def get_now_offset_time(default_offset=3):
    return get_date_offset(default_offset).time()


def round_to_nearset_minute(dt):
    return dt.replace(second=0, microsecond=0)