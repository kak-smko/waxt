"""Property-based tests using ``hypothesis`` (requirement #8)."""

from __future__ import annotations

import datetime

import pytest
from hypothesis import given
from hypothesis import strategies as st

from tests.conftest import FULL_RANGE_JALALI_YEAR_END, FULL_RANGE_JALALI_YEAR_START
from waxt.calendar_converters import JalaliCalendar

pytestmark = pytest.mark.property

gregorian_dates_in_range = st.dates(
    min_value=datetime.date(1600, 1, 1),
    max_value=datetime.date(2500, 12, 31),
)


@st.composite
def valid_jalali_dates(draw):
    year = draw(
        st.integers(
            min_value=FULL_RANGE_JALALI_YEAR_START,
            max_value=FULL_RANGE_JALALI_YEAR_END,
        )
    )
    month = draw(st.integers(min_value=1, max_value=12))
    if month <= 6:
        max_day = 31
    elif month <= 11:
        max_day = 30
    else:
        max_day = 30 if JalaliCalendar.is_leap(year) else 29
    day = draw(st.integers(min_value=1, max_value=max_day))
    return (year, month, day)


@given(gregorian_dates_in_range)
def test_property_gregorian_round_trip(date_):
    j = JalaliCalendar.gregorian_to_jalali(date_.year, date_.month, date_.day)
    assert JalaliCalendar.jalali_to_gregorian(*j) == (
        date_.year,
        date_.month,
        date_.day,
    )


@given(valid_jalali_dates())
def test_property_jalali_round_trip(j_date):
    g = JalaliCalendar.jalali_to_gregorian(*j_date)
    assert JalaliCalendar.gregorian_to_jalali(*g) == j_date


@given(gregorian_dates_in_range)
def test_property_jalali_components_are_structurally_valid(date_):
    j_year, j_month, j_day = JalaliCalendar.gregorian_to_jalali(
        date_.year, date_.month, date_.day
    )
    assert 1 <= j_month <= 12
    if j_month <= 6:
        assert 1 <= j_day <= 31
    elif j_month <= 11:
        assert 1 <= j_day <= 30
    else:
        assert 1 <= j_day <= (30 if JalaliCalendar.is_leap(j_year) else 29)


@given(
    st.dates(
        min_value=datetime.date(1600, 1, 1),
        max_value=datetime.date(2500, 12, 30),
    )
)
def test_property_consecutive_days_are_monotonically_increasing_in_jalali(date_):
    next_date = date_ + datetime.timedelta(days=1)

    j1 = JalaliCalendar.gregorian_to_jalali(date_.year, date_.month, date_.day)
    j2 = JalaliCalendar.gregorian_to_jalali(
        next_date.year, next_date.month, next_date.day
    )
    assert j2 > j1


@given(
    st.integers(
        min_value=FULL_RANGE_JALALI_YEAR_START, max_value=FULL_RANGE_JALALI_YEAR_END
    )
)
def test_property_year_length_matches_is_leap(year):
    nowruz = JalaliCalendar.jalali_to_gregorian(year, 1, 1)
    next_nowruz = JalaliCalendar.jalali_to_gregorian(year + 1, 1, 1)
    days_in_year = (datetime.date(*next_nowruz) - datetime.date(*nowruz)).days
    expected = 366 if JalaliCalendar.is_leap(year) else 365
    assert days_in_year == expected
