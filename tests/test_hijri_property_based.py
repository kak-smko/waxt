"""Property-based tests for ``HijriCalendar`` using ``hypothesis``
(requirement #9)."""

from __future__ import annotations

import datetime

import pytest
from hypothesis import given
from hypothesis import strategies as st

from tests.conftest import (
    FULL_RANGE_HIJRI_YEAR_END,
    FULL_RANGE_HIJRI_YEAR_START,
    hijri_days_in_month,
)
from waxt.calendar_converters import HijriCalendar

pytestmark = [pytest.mark.property, pytest.mark.hijri]

gregorian_dates_in_range = st.dates(
    min_value=datetime.date(1600, 1, 1),
    max_value=datetime.date(2500, 12, 31),
)


@st.composite
def valid_hijri_dates(draw):
    year = draw(
        st.integers(
            min_value=FULL_RANGE_HIJRI_YEAR_START,
            max_value=FULL_RANGE_HIJRI_YEAR_END,
        )
    )
    month = draw(st.integers(min_value=1, max_value=12))
    max_day = hijri_days_in_month(year, month)
    day = draw(st.integers(min_value=1, max_value=max_day))
    return (year, month, day)


@given(gregorian_dates_in_range)
def test_property_gregorian_round_trip(date_):
    h = HijriCalendar.gregorian_to_hijri(date_.year, date_.month, date_.day)
    assert HijriCalendar.hijri_to_gregorian(*h) == (
        date_.year,
        date_.month,
        date_.day,
    )


@given(valid_hijri_dates())
def test_property_hijri_round_trip(h_date):
    g = HijriCalendar.hijri_to_gregorian(*h_date)
    assert HijriCalendar.gregorian_to_hijri(*g) == h_date


@given(gregorian_dates_in_range)
def test_property_hijri_components_are_structurally_valid(date_):
    h_year, h_month, h_day = HijriCalendar.gregorian_to_hijri(
        date_.year, date_.month, date_.day
    )
    assert 1 <= h_month <= 12
    assert 1 <= h_day <= hijri_days_in_month(h_year, h_month)


@given(
    st.dates(
        min_value=datetime.date(1600, 1, 1),
        max_value=datetime.date(2500, 12, 30),
    )
)
def test_property_consecutive_days_are_monotonically_increasing_in_hijri(date_):
    next_date = date_ + datetime.timedelta(days=1)

    h1 = HijriCalendar.gregorian_to_hijri(date_.year, date_.month, date_.day)
    h2 = HijriCalendar.gregorian_to_hijri(
        next_date.year, next_date.month, next_date.day
    )
    assert h2 > h1


@given(
    st.integers(
        min_value=FULL_RANGE_HIJRI_YEAR_START, max_value=FULL_RANGE_HIJRI_YEAR_END
    )
)
def test_property_year_length_matches_is_leap(year):
    new_year = HijriCalendar.hijri_to_gregorian(year, 1, 1)
    next_new_year = HijriCalendar.hijri_to_gregorian(year + 1, 1, 1)
    days_in_year = (datetime.date(*next_new_year) - datetime.date(*new_year)).days
    expected = 355 if HijriCalendar.is_leap(year) else 354
    assert days_in_year == expected


@given(
    st.integers(
        min_value=FULL_RANGE_HIJRI_YEAR_START, max_value=FULL_RANGE_HIJRI_YEAR_END
    ),
    st.integers(min_value=1, max_value=12),
)
def test_property_month_length_is_29_or_30(year, month):
    max_day = hijri_days_in_month(year, month)
    assert max_day in (29, 30)

    g_last = HijriCalendar.hijri_to_gregorian(year, month, max_day)
    with pytest.raises(ValueError):
        HijriCalendar.hijri_to_gregorian(year, month, max_day + 1)

    # The day after the last valid day of the month must belong to the
    # next month (or next year, for month 12).
    next_g = datetime.date(*g_last) + datetime.timedelta(days=1)
    h_next = HijriCalendar.gregorian_to_hijri(next_g.year, next_g.month, next_g.day)
    if month == 12:
        assert h_next == (year + 1, 1, 1)
    else:
        assert h_next == (year, month + 1, 1)
