"""Hijri year-boundary tests (requirements #5 and #6).

For a broad sample of Hijri years, this module checks:

* the day *before* 1 Muharram (last day of the previous Hijri year - 29 or
  30 Dhu al-Hijjah, depending on whether the previous year is a leap
  year),
* 1 Muharram itself (the new year),
* the day *after* 1 Muharram (2 Muharram),

in both directions (Gregorian -> Hijri and Hijri -> Gregorian), ensuring
full internal consistency across the year boundary - i.e. the exact "29 or
30 Dhu al-Hijjah rolls over to 1 Muharram" transition called out by
requirement #6.
"""

from __future__ import annotations

import datetime

import pytest

from waxt.calendar_converters import HijriCalendar

# A representative sample of Hijri years spanning the required range,
# including both leap and non-leap years on either side of the boundary.
HIJRI_YEARS_FOR_NEW_YEAR = [
    1,
    2,
    3,
    9,
    10,
    100,
    500,
    999,
    1000,
    1300,
    1399,
    1400,
    1401,
    1444,
    1445,
    1446,
    1447,
    1500,
]

#: Same as above, but excluding Hijri year 1: the day *before* 1 Muharram
#: AH 1 is before the calendar's epoch, where ``gregorian_to_hijri`` raises
#: ValueError instead of returning a "real" previous-year date (see
#: ``test_hijri_basic.py`` and ``test_hijri_invalid_inputs.py``).
HIJRI_YEARS_WITH_REAL_PREVIOUS_YEAR = [y for y in HIJRI_YEARS_FOR_NEW_YEAR if y != 1]


def test_day_before_epoch_new_year_raises():
    """AH 1 has no real predecessor: the day before 1 Muharram AH 1 is
    before the calendar's epoch, so ``gregorian_to_hijri`` raises ValueError
    rather than returning e.g. ``(0, 12, 30)``."""
    new_year_date = datetime.date(*HijriCalendar.hijri_to_gregorian(1, 1, 1))
    day_before = new_year_date - datetime.timedelta(days=1)
    with pytest.raises(ValueError, match="Date is before Hijri epoch"):
        HijriCalendar.gregorian_to_hijri(
            day_before.year, day_before.month, day_before.day
        )


@pytest.mark.parametrize("hijri_year", HIJRI_YEARS_WITH_REAL_PREVIOUS_YEAR)
def test_new_year_day_before_on_and_after(hijri_year):
    new_year_g = HijriCalendar.hijri_to_gregorian(hijri_year, 1, 1)
    new_year_date = datetime.date(*new_year_g)

    day_before = new_year_date - datetime.timedelta(days=1)
    day_after = new_year_date + datetime.timedelta(days=1)

    # 1 Muharram itself.
    assert HijriCalendar.gregorian_to_hijri(*new_year_g) == (hijri_year, 1, 1)

    # Day after: 2 Muharram of the same Hijri year.
    h_after = HijriCalendar.gregorian_to_hijri(
        day_after.year, day_after.month, day_after.day
    )
    assert h_after == (hijri_year, 1, 2)
    assert HijriCalendar.hijri_to_gregorian(*h_after) == (
        day_after.year,
        day_after.month,
        day_after.day,
    )

    # Day before: last day of Dhu al-Hijjah of the previous Hijri year.
    previous_year = hijri_year - 1
    expected_last_day = 30 if HijriCalendar.is_leap(previous_year) else 29
    h_before = HijriCalendar.gregorian_to_hijri(
        day_before.year, day_before.month, day_before.day
    )
    assert h_before == (previous_year, 12, expected_last_day)
    assert HijriCalendar.hijri_to_gregorian(*h_before) == (
        day_before.year,
        day_before.month,
        day_before.day,
    )


@pytest.mark.parametrize("hijri_year", HIJRI_YEARS_FOR_NEW_YEAR)
def test_hijri_year_end_and_start_are_contiguous(hijri_year):
    """29/30 Dhu al-Hijjah of ``hijri_year`` must be immediately followed
    by 1 Muharram of ``hijri_year + 1``, with no gap or overlap - the
    "year change" scenario explicitly called out by requirement #6."""
    last_day = 30 if HijriCalendar.is_leap(hijri_year) else 29
    g_last_day = HijriCalendar.hijri_to_gregorian(hijri_year, 12, last_day)
    g_next_new_year = HijriCalendar.hijri_to_gregorian(hijri_year + 1, 1, 1)

    expected_next_day = datetime.date(*g_last_day) + datetime.timedelta(days=1)
    assert g_next_new_year == (
        expected_next_day.year,
        expected_next_day.month,
        expected_next_day.day,
    )


@pytest.mark.parametrize("hijri_year", HIJRI_YEARS_FOR_NEW_YEAR)
def test_hijri_year_has_354_or_355_days(hijri_year):
    """A Hijri year must have exactly 354 days (common) or 355 days
    (leap), matching ``is_leap`` - never any other length."""
    start = datetime.date(*HijriCalendar.hijri_to_gregorian(hijri_year, 1, 1))
    end = datetime.date(*HijriCalendar.hijri_to_gregorian(hijri_year + 1, 1, 1))
    length = (end - start).days
    expected = 355 if HijriCalendar.is_leap(hijri_year) else 354
    assert length == expected


@pytest.mark.parametrize(
    "hijri_year, day_offset",
    [(y, offset) for y in (2, 1400, 1445, 1446) for offset in range(-2, 3)]
    # Hijri year 1 has no real predecessor (see
    # test_day_before_epoch_new_year_clamps_to_sentinel above), so only
    # non-negative offsets are meaningful for it.
    + [(1, offset) for offset in range(0, 3)],
)
def test_dates_around_year_boundary_are_strictly_sequential(hijri_year, day_offset):
    """Every day within +/-2 of a Hijri new year must map to a strictly
    increasing sequence with no duplicates or reordering."""
    new_year_g = datetime.date(*HijriCalendar.hijri_to_gregorian(hijri_year, 1, 1))
    day = new_year_g + datetime.timedelta(days=day_offset)
    next_day = day + datetime.timedelta(days=1)

    h_day = HijriCalendar.gregorian_to_hijri(day.year, day.month, day.day)
    h_next = HijriCalendar.gregorian_to_hijri(
        next_day.year, next_day.month, next_day.day
    )
    assert h_next > h_day
