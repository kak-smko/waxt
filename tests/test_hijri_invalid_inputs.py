"""Invalid-input tests for ``HijriCalendar`` (requirement #7).

IMPORTANT - documented findings / assumptions
----------------------------------------------
Reading ``HijriCalendar`` before writing this suite surfaced several
concrete, sometimes surprising, behaviours. These tests intentionally
codify the *current* behaviour (so any future change is caught as an
explicit, visible diff), and each surprising case is called out below so
the maintainer can decide whether it should become an enhancement.

1. ``hijri_to_gregorian`` validates ``h_month`` (must be 1-12) and
   ``h_day`` (must be within the correct range for that month/leap year)
   and raises ``ValueError`` with a clear message on violation.

2. ``hijri_to_gregorian`` performs **no validation at all** on ``h_year``.
   ``h_year=0`` and negative years are silently accepted and produce a
   pre-epoch Gregorian date (as long as it stays within
   ``datetime.date``'s year 1-9999 range - see
   ``test_hijri_support_boundaries.py`` for exactly where it eventually
   raises ``OverflowError``/``ValueError`` instead).

3. ``gregorian_to_hijri`` delegates all of its own validation to
   ``datetime.date(year, month, day)``, so invalid Gregorian
   month/day/type combinations raise whatever ``datetime.date`` itself
   raises (``ValueError`` for out-of-range values, ``TypeError`` for
   non-integer types) rather than a ``HijriCalendar``-specific message.

4. Passing ``None`` or a ``str`` for *any* of ``h_year``/``h_month``/
   ``h_day`` raises ``TypeError`` in ``hijri_to_gregorian``, because the
   code performs comparisons/arithmetic directly on the argument.

5. Passing a ``float`` behaves inconsistently across parameters:
   * ``h_month`` as a float (even a "whole" one like ``1.0``) raises
     ``TypeError``, because it is later passed to the builtin ``range()``,
     which requires an ``int``.
   * ``h_year`` and ``h_day`` as floats do **not** raise: they flow
     straight into comparisons/arithmetic/``timedelta(days=...)`` (all of
     which happily accept floats), silently producing a plausible-looking
     but not-quite-integral result. This is a genuine validation gap, not
     a deliberate feature - flagged here for transparency.

6. Dates before the Hijri epoch (622-07-19) passed to ``gregorian_to_hijri``
   raise ``ValueError`` (already covered by ``test_hijri_basic.py``;
   re-asserted here for completeness next to the rest of the invalid-input
   matrix).
"""

from __future__ import annotations

import pytest

from waxt.calendar_converters import HijriCalendar

# ---------------------------------------------------------------------------
# hijri_to_gregorian: validated inputs -> ValueError
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "month", [0, -1, 13, 14, 100, -100], ids=lambda m: f"month={m}"
)
def test_hijri_to_gregorian_rejects_invalid_month(month):
    with pytest.raises(ValueError, match="Invalid Hijri month"):
        HijriCalendar.hijri_to_gregorian(1445, month, 1)


@pytest.mark.parametrize(
    "h_year, month, day",
    [
        (1445, 1, 0),  # day zero
        (1445, 1, -1),  # negative day
        (1445, 1, 31),  # 30-day (odd) month, one day too many
        (1445, 2, 30),  # 29-day (even, non-Dhu-al-Hijjah) month, one too many
        (1445, 12, 30),  # 30 Dhu al-Hijjah in a non-leap year (1445 is non-leap)
        (1401, 12, 30),  # 30 Dhu al-Hijjah in a non-leap year (1401 is non-leap)
        (1446, 12, 31),  # Dhu al-Hijjah never has 31 days, even in a leap year
    ],
    ids=[
        "day=0",
        "day=-1",
        "30-day-month day=31",
        "29-day-month day=30",
        "30-Dhul-Hijjah-non-leap-1445",
        "30-Dhul-Hijjah-non-leap-1401",
        "31-Dhul-Hijjah-leap-1446",
    ],
)
def test_hijri_to_gregorian_rejects_invalid_day(h_year, month, day):
    with pytest.raises(ValueError, match="Invalid Hijri day"):
        HijriCalendar.hijri_to_gregorian(h_year, month, day)


def test_hijri_to_gregorian_accepts_30_dhul_hijjah_in_leap_year():
    # Sanity check companion to the invalid-day tests above: 1446 IS leap.
    assert HijriCalendar.is_leap(1446) is True
    assert HijriCalendar.hijri_to_gregorian(1446, 12, 30) == (2025, 6, 27)


# ---------------------------------------------------------------------------
# hijri_to_gregorian: invalid types -> TypeError (year, month, day)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bad_year", [None, "1445", [1445], {1445}, object()])
def test_hijri_to_gregorian_rejects_non_numeric_year(bad_year):
    with pytest.raises(TypeError):
        HijriCalendar.hijri_to_gregorian(bad_year, 1, 1)


@pytest.mark.parametrize("bad_month", [None, "1", [1], object()])
def test_hijri_to_gregorian_rejects_non_numeric_month(bad_month):
    with pytest.raises(TypeError):
        HijriCalendar.hijri_to_gregorian(1445, bad_month, 1)


@pytest.mark.parametrize("bad_day", [None, "1", [1], object()])
def test_hijri_to_gregorian_rejects_non_numeric_day(bad_day):
    with pytest.raises(TypeError):
        HijriCalendar.hijri_to_gregorian(1445, 1, bad_day)


@pytest.mark.parametrize("bad_month", [1.0, 1.5, 12.0])
def test_hijri_to_gregorian_rejects_float_month(bad_month):
    """Unlike year/day, ``h_month`` is passed to ``range()`` internally,
    which raises ``TypeError`` for any float, even a "whole" one."""
    with pytest.raises(TypeError):
        HijriCalendar.hijri_to_gregorian(1445, bad_month, 1)


# ---------------------------------------------------------------------------
# hijri_to_gregorian: documents the *lack* of validation for h_year,
# and the silent acceptance of float h_year/h_day.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", [0, -1, -100])
def test_hijri_to_gregorian_does_not_validate_year_is_positive(year):
    """``h_year`` has no ``>= 1`` guard: zero and negative years are
    silently accepted and produce a pre-epoch Gregorian date instead of
    raising ``ValueError``. This documents current behaviour explicitly."""
    result = HijriCalendar.hijri_to_gregorian(year, 1, 1)
    assert isinstance(result, tuple)
    assert len(result) == 3
    # It must, at least, be strictly before the real epoch.
    assert result < (622, 7, 19)


def test_hijri_to_gregorian_silently_accepts_float_year():
    result_int = HijriCalendar.hijri_to_gregorian(1445, 1, 1)
    result_float = HijriCalendar.hijri_to_gregorian(1445.0, 1, 1)
    assert result_float == result_int


def test_hijri_to_gregorian_silently_accepts_float_day():
    """A float day does not raise (comparisons and ``timedelta`` both
    accept floats); it silently participates in the arithmetic instead of
    being rejected as a non-integral value."""
    result = HijriCalendar.hijri_to_gregorian(1445, 1, 1.0)
    assert result == HijriCalendar.hijri_to_gregorian(1445, 1, 1)

    # A genuinely fractional day is accepted too and produces a date
    # consistent with truncating/flooring the fractional day count.
    fractional_result = HijriCalendar.hijri_to_gregorian(1445, 1, 1.9)
    assert fractional_result in (
        HijriCalendar.hijri_to_gregorian(1445, 1, 1),
        HijriCalendar.hijri_to_gregorian(1445, 1, 2),
    )


# ---------------------------------------------------------------------------
# gregorian_to_hijri: delegates validation to datetime.date
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "g_year, g_month, g_day",
    [
        (2024, 13, 1),  # month 13
        (2024, 0, 1),  # month 0
        (2024, 1, 0),  # day 0
        (2024, 1, 32),  # day 32 in January
        (2024, 2, 30),  # "Feb 30" (leap year, still invalid)
        (2023, 2, 29),  # "Feb 29" in a non-leap year
        (2024, 4, 31),  # "Apr 31"
    ],
    ids=[
        "month=13",
        "month=0",
        "day=0",
        "day=32",
        "feb-30-leap-year",
        "feb-29-non-leap-year",
        "apr-31",
    ],
)
def test_gregorian_to_hijri_rejects_calendar_invalid_dates(g_year, g_month, g_day):
    """Unlike ``JalaliCalendar.gregorian_to_jalali`` (which has no range
    checks at all), ``HijriCalendar.gregorian_to_hijri`` builds a real
    ``datetime.date`` internally, so invalid Gregorian dates *do* raise -
    with Python's own ``ValueError`` message, not a Hijri-specific one."""
    with pytest.raises(ValueError):
        HijriCalendar.gregorian_to_hijri(g_year, g_month, g_day)


@pytest.mark.parametrize("bad_year", [None, "2024", [2024], object()])
def test_gregorian_to_hijri_rejects_non_numeric_year(bad_year):
    with pytest.raises(TypeError):
        HijriCalendar.gregorian_to_hijri(bad_year, 1, 1)


@pytest.mark.parametrize("bad_month", [None, "1", [1], object()])
def test_gregorian_to_hijri_rejects_non_numeric_month(bad_month):
    with pytest.raises(TypeError):
        HijriCalendar.gregorian_to_hijri(2024, bad_month, 1)


@pytest.mark.parametrize("bad_day", [None, "1", [1], object()])
def test_gregorian_to_hijri_rejects_non_numeric_day(bad_day):
    with pytest.raises(TypeError):
        HijriCalendar.gregorian_to_hijri(2024, 1, bad_day)


@pytest.mark.parametrize("field", ["year", "month", "day"])
def test_gregorian_to_hijri_rejects_float_inputs(field):
    """Unlike ``hijri_to_gregorian``, every argument of
    ``gregorian_to_hijri`` flows into ``datetime.date(...)``, which rejects
    floats outright (including "whole" floats like ``2024.0``) with a
    ``TypeError`` - so, unlike the Hijri-side float gap documented above,
    there is no silent-acceptance issue on the Gregorian side."""
    args = {"year": 2024, "month": 1, "day": 1}
    args[field] = float(args[field])
    with pytest.raises(TypeError):
        HijriCalendar.gregorian_to_hijri(args["year"], args["month"], args["day"])


# ---------------------------------------------------------------------------
# gregorian_to_hijri: pre-epoch sentinel behaviour
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "g_year, g_month, g_day",
    [(600, 1, 1), (1, 1, 1), (621, 12, 31), (622, 7, 18)],
)
def test_gregorian_to_hijri_before_epoch_raises(g_year, g_month, g_day):
    """Documented current behaviour: any Gregorian date strictly before
    the Hijri epoch (622-07-19) raises ValueError."""
    with pytest.raises(ValueError, match="Date is before Hijri epoch"):
        HijriCalendar.gregorian_to_hijri(g_year, g_month, g_day)


# ---------------------------------------------------------------------------
# is_leap: invalid inputs
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bad_year", [None, "1445", [1445], object()])
def test_is_leap_rejects_non_numeric_year(bad_year):
    with pytest.raises(TypeError):
        HijriCalendar.is_leap(bad_year)


def test_is_leap_silently_accepts_float_year():
    """``is_leap`` uses only ``%`` and comparisons, both of which accept
    floats without complaint."""
    assert HijriCalendar.is_leap(1400.0) == HijriCalendar.is_leap(1400)
