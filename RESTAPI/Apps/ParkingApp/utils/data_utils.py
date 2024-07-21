from datetime import datetime, timezone, timedelta


def get_timezone_delta() -> timedelta:
    # local datetime
    d1 = datetime.now()
    # utc datetime
    d2 = datetime.fromisoformat(datetime.now(timezone.utc).isoformat()[:26])
    return d2 - d1


def utc_to_local(datetime_value):
    datetime_value = datetime.fromisoformat(datetime_value.isoformat()[:26])
    time_delta = get_timezone_delta()
    return datetime_value - time_delta


def local_to_utc(datetime_value):
    datetime_value = datetime.fromisoformat(datetime_value.isoformat()[:26])
    time_delta = get_timezone_delta()
    return datetime_value + time_delta
