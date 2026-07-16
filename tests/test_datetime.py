import pickle
from datetime import date, datetime, time, timedelta, timezone

import pytest

from waxt import DateTime, tzinfo
from waxt.datetime import datetime as waxt_datetime


def test_constructor_and_stdlib_interop() -> None:
    value = DateTime(2025, 6, 15, 14, 30, 45, 123456)

    assert value.to_datetime() == datetime(2025, 6, 15, 14, 30, 45, 123456)
    assert (value.year, value.month, value.day) == (2025, 6, 15)
    assert (value.hour, value.minute, value.second, value.microsecond) == (
        14,
        30,
        45,
        123456,
    )
    assert waxt_datetime is DateTime


def test_jalali_and_hijri_construction_and_conversion() -> None:
    jalali = DateTime(1404, 3, 25, 14, 30, calendar="jalali")
    gregorian = jalali.to_calendar("gregorian")
    hijri = jalali.to_calendar("hijri")

    assert jalali.to_datetime() == datetime(2025, 6, 15, 14, 30)
    assert (gregorian.year, gregorian.month, gregorian.day) == (2025, 6, 15)
    assert hijri.to_datetime() == jalali.to_datetime()
    assert hijri.calendar == "hijri"
    assert jalali == gregorian == hijri
    assert hash(jalali) == hash(gregorian)


def test_invalid_calendar_and_calendar_date_are_rejected() -> None:
    with pytest.raises(ValueError, match="Invalid calendar"):
        DateTime(2025, 1, 1, calendar="unknown")
    with pytest.raises(ValueError):
        DateTime(1404, 12, 30, calendar="jalali")


def test_standard_constructors() -> None:
    source = datetime(2025, 6, 15, 14, 30, tzinfo=timezone.utc)
    value = DateTime.from_datetime(source, calendar="jalali")

    assert DateTime.fromtimestamp(source.timestamp(), timezone.utc) == source
    assert DateTime.utcfromtimestamp(0).to_datetime() == datetime(1970, 1, 1)
    assert DateTime.fromordinal(source.toordinal()).date() == source.date()
    assert DateTime.combine(value, time(9, 10)).calendar == "jalali"
    assert DateTime.combine(date(2025, 6, 15), time(9, 10)).to_datetime() == datetime(
        2025, 6, 15, 9, 10
    )


def test_iso_parsing_and_formatting_use_selected_calendar() -> None:
    value = DateTime.fromisoformat(
        "1404-03-25T14:30:45.123456+03:30", calendar="jalali"
    )

    assert value.to_datetime() == datetime(
        2025, 6, 15, 14, 30, 45, 123456, timezone(timedelta(hours=3, minutes=30))
    )
    assert value.isoformat() == "1404-03-25T14:30:45.123456+03:30"
    assert value.isoformat(" ", "minutes") == "1404-03-25 14:30+03:30"
    assert str(value) == "1404-03-25 14:30:45.123456+03:30"


def test_strptime_strftime_and_format() -> None:
    value = DateTime.strptime(
        "1404/03/25 14:30:45 +0330",
        "%Y/%m/%d %H:%M:%S %z",
        calendar="jalali",
    )

    assert value.strftime("%Y-%m-%d %H:%M:%S %z") == ("1404-03-25 14:30:45 +0330")
    assert value.strftime("%j %B %%") == "087 Khordad %"
    assert f"{value:%Y/%m/%d}" == "1404/03/25"


def test_replace_is_immutable_and_uses_calendar_fields() -> None:
    value = DateTime(1404, 3, 25, 14, 30, calendar="jalali")
    changed = value.replace(day=26, minute=45)

    assert (changed.year, changed.month, changed.day, changed.minute) == (
        1404,
        3,
        26,
        45,
    )
    assert value.day == 25
    with pytest.raises(AttributeError):
        value._calendar = "gregorian"


def test_timedelta_arithmetic_and_comparisons() -> None:
    value = DateTime(1404, 12, 29, calendar="jalali")
    next_day = value + timedelta(days=1)

    assert (next_day.year, next_day.month, next_day.day) == (1405, 1, 1)
    assert next_day - value == timedelta(days=1)
    assert next_day - timedelta(days=1) == value
    assert timedelta(days=1) + value == next_day
    assert value < next_day
    assert value == value.to_datetime()
    assert datetime(2026, 3, 20) - value.to_calendar("gregorian") == timedelta(0)


def test_add_days_and_months_use_selected_calendar() -> None:
    timezone_info = timezone(timedelta(hours=3, minutes=30))
    gregorian = DateTime(2024, 1, 31, 12, 13, 14, 123456, timezone_info, fold=1)
    jalali = DateTime(1404, 6, 31, calendar="jalali")
    hijri = DateTime(1446, 1, 30, calendar="hijri")

    next_day = jalali.add_days(1)
    next_month = gregorian.add_months(1)

    assert (next_day.year, next_day.month, next_day.day) == (1404, 7, 1)
    assert next_day.calendar == "jalali"
    assert (next_month.year, next_month.month, next_month.day) == (2024, 2, 29)
    assert next_month.to_datetime().timetz() == gregorian.to_datetime().timetz()
    assert next_month.fold == gregorian.fold
    assert (jalali.add_months(1).year, jalali.add_months(1).month) == (1404, 7)
    assert jalali.add_months(1).day == 30
    assert (hijri.add_months(1).year, hijri.add_months(1).month) == (1446, 2)
    assert hijri.add_months(1).day == 29
    assert (
        DateTime(2025, 1, 31).add_months(-1).year,
        DateTime(2025, 1, 31).add_months(-1).month,
    ) == (2024, 12)


def test_pickle_round_trip_preserves_calendar() -> None:
    value = DateTime(1404, 3, 25, 14, 30, calendar="jalali")

    restored = pickle.loads(pickle.dumps(value))

    assert restored == value
    assert restored.calendar == "jalali"


def test_timezone_methods_retain_calendar() -> None:
    value = DateTime(
        1404,
        3,
        25,
        12,
        tzinfo=timezone.utc,
        calendar="jalali",
    )
    local = value.astimezone(timezone(timedelta(hours=3, minutes=30)))

    assert local.calendar == "jalali"
    assert local.hour == 15
    assert local.minute == 30
    assert local.utcoffset() == timedelta(hours=3, minutes=30)
    assert local.timestamp() == value.timestamp()
    assert local.utctimetuple().tm_hour == 12


def test_standard_calendar_methods_delegate_to_absolute_gregorian_date() -> None:
    value = DateTime(1404, 3, 25, calendar="jalali")
    source = datetime(2025, 6, 15)

    assert value.date() == source.date()
    assert value.toordinal() == source.toordinal()
    assert value.weekday() == source.weekday()
    assert value.isoweekday() == source.isoweekday()
    assert value.isocalendar() == tuple(source.isocalendar())
    assert value.timetuple().tm_yday == 87
