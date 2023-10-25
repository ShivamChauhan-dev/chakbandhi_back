import datetime


def first_and_last_day_of_this_month() -> tuple:
    today_date = datetime.date.today()
    first_day = today_date.replace(day=1)
    next_month = first_day.replace(day=28) + datetime.timedelta(days=4)
    last_day = next_month - datetime.timedelta(days=next_month.day)
    return first_day, last_day


def date_range(from_date: datetime, to_date: datetime = None) -> list[datetime.date]:
    to_date = to_date or datetime.date.today()
    delta = datetime.timedelta(days=1)
    from_date_copy = from_date
    dates = []
    while from_date_copy <= to_date:
        dates.append(from_date_copy)
        from_date_copy += delta

    return dates
