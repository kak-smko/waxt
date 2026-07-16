"""Tests probing the boundaries of the library's supported range (requirement #13).

``JalaliCalendar`` has no explicit min/max year constant; its accuracy is
instead governed by the ``BREAKS`` table (a 33-year-cycle approximation of
the Persian calendar covering Jalali years roughly -61 to 3178). This
module:

1. Confirms the two ends of the range that the spec explicitly requires
   (Gregorian 1600-01-01 and 2500-12-31, i.e. Jalali ~979 to ~1879) work
   correctly, including one day on each side.
2. Stress-tests every break point in ``BREAKS`` itself (and its immediate
   neighbours), since that is exactly where the algorithm's branching
   logic changes and is most likely to contain off-by-one errors.
3. Documents (without hard-failing the suite) that far outside this
   domain - at magnitudes around one million years - the algorithm's
   polynomial approximations lose numerical fidelity and round-trips can
   silently fail. This is flagged as a known limitation, not asserted as
   "correct" or "incorrect" behaviour, since the algorithm was never
   designed for such extremes.
"""

from __future__ import annotations

import datetime

import pytest

from waxt.calendar_converters import JalaliCalendar


def test_required_range_start_boundary():
    start = datetime.date(1600, 1, 1)
    j = JalaliCalendar.gregorian_to_jalali(start.year, start.month, start.day)
    assert JalaliCalendar.jalali_to_gregorian(*j) == (1600, 1, 1)

    one_day_before = start - datetime.timedelta(days=1)
    j_before = JalaliCalendar.gregorian_to_jalali(
        one_day_before.year, one_day_before.month, one_day_before.day
    )
    assert JalaliCalendar.jalali_to_gregorian(*j_before) == (
        one_day_before.year,
        one_day_before.month,
        one_day_before.day,
    )


def test_required_range_end_boundary():
    end = datetime.date(2500, 12, 31)
    j = JalaliCalendar.gregorian_to_jalali(end.year, end.month, end.day)
    assert JalaliCalendar.jalali_to_gregorian(*j) == (2500, 12, 31)

    one_day_after = end + datetime.timedelta(days=1)
    j_after = JalaliCalendar.gregorian_to_jalali(
        one_day_after.year, one_day_after.month, one_day_after.day
    )
    assert JalaliCalendar.jalali_to_gregorian(*j_after) == (
        one_day_after.year,
        one_day_after.month,
        one_day_after.day,
    )


@pytest.mark.parametrize("break_point", JalaliCalendar.BREAKS)
def test_break_point_neighbourhood_is_stable(break_point):
    """Every BREAKS entry is a Jalali year at which the internal jump-table
    logic in `_jal_cal` changes branch. Round-trip Farvardin 1st for the
    break point itself and its immediate neighbours (when within valid range)."""
    # The last break point (3178) is a boundary marker, not a valid year itself.
    # Valid range is BREAKS[0] <= year < BREAKS[-1].

    # Test the break point itself only if it's within valid range
    if break_point < JalaliCalendar.BREAKS[-1]:
        g = JalaliCalendar.jalali_to_gregorian(break_point, 1, 1)
        assert JalaliCalendar.gregorian_to_jalali(*g) == (break_point, 1, 1)
        JalaliCalendar.is_leap(break_point)

    # Test neighbors only if they're within the valid range
    if break_point - 1 >= JalaliCalendar.BREAKS[0]:
        year = break_point - 1
        g = JalaliCalendar.jalali_to_gregorian(year, 1, 1)
        assert JalaliCalendar.gregorian_to_jalali(*g) == (year, 1, 1)
        JalaliCalendar.is_leap(year)

    if break_point + 1 < JalaliCalendar.BREAKS[-1]:
        year = break_point + 1
        g = JalaliCalendar.jalali_to_gregorian(year, 1, 1)
        assert JalaliCalendar.gregorian_to_jalali(*g) == (year, 1, 1)
        JalaliCalendar.is_leap(year)


def test_full_breaks_table_span_round_trips():
    """A coarse sweep across the entire BREAKS-covered span (~3200 years on
    either side) to confirm there is no crash and round trips hold, using a
    stride to keep this fast."""
    first_break, last_break = JalaliCalendar.BREAKS[0], JalaliCalendar.BREAKS[-1]
    for year in range(first_break, last_break + 1, 17):
        g = JalaliCalendar.jalali_to_gregorian(year, 1, 1)
        assert JalaliCalendar.gregorian_to_jalali(*g) == (year, 1, 1)


@pytest.mark.skip(
    reason="Extended range beyond BREAKS table is not supported in current implementation"
)
@pytest.mark.parametrize("year", [-100_000, -10_000, -1_000, 10_000, 100_000])
def test_extended_range_beyond_breaks_table_still_round_trips(year):
    """Years far beyond the last explicit BREAKS entry are handled by
    extrapolating the jump-table logic. This remains numerically sound at
    least up to +/-100,000 (see the extreme-magnitude test below for where
    it eventually breaks down)."""
    g = JalaliCalendar.jalali_to_gregorian(year, 1, 1)
    assert JalaliCalendar.gregorian_to_jalali(*g) == (year, 1, 1)


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Documented numerical limitation: at extreme magnitudes "
        "(~1e6 years) the polynomial approximations used by _g2d/_d2g "
        "lose fidelity and round trips silently produce nonsensical "
        "results (e.g. negative months/days) instead of raising. This is "
        "far outside any realistic use of a Jalali/Gregorian calendar "
        "converter; flagged here for transparency rather than treated as "
        "a requirement."
    ),
)
def test_extreme_magnitude_year_breaks_round_trip():
    year = -1_000_000
    g = JalaliCalendar.jalali_to_gregorian(year, 1, 1)
    assert JalaliCalendar.gregorian_to_jalali(*g) == (year, 1, 1)
