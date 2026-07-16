"""Invalid-input tests (requirement #6).

IMPORTANT - documented finding / assumption
--------------------------------------------
While analysing ``JalaliCalendar`` before writing this suite, we found that
input validation is **asymmetric** between the two conversion functions:

* ``jalali_to_gregorian`` validates ``j_month`` (must be 1-12) and
  ``j_day`` (must be within the correct range for that month/leap year)
  and raises ``ValueError`` on violation.
* ``gregorian_to_jalali`` performs **no validation at all**. Passing
  ``month=13``, ``month=0``, ``day=0``, ``day=32``, "Feb 30" or "Apr 31"
  does not raise - it silently returns an arithmetically-derived (and
  meaningless) result, because the underlying Julian Day Number formula
  (``_g2d``) has no domain checks.
* Passing ``None`` or a ``str`` for the *year* argument raises
  ``TypeError`` in both functions (because the code performs arithmetic
  directly on it), but passing ``None``/``str`` for *month*/*day* only
  raises in ``jalali_to_gregorian`` (because that is the function that
  actually compares them with ``<=``); ``gregorian_to_jalali`` does not
  compare month/day against anything, so those bad types silently flow
  into arithmetic and either raise a ``TypeError`` (e.g. for ``str``) or,
  for ``float``, do **not** raise and instead return float-valued tuples.

These tests intentionally codify the *current* behaviour so any future
change is caught as an explicit, visible diff rather than a silent
behavioural change. If stricter validation of ``gregorian_to_jalali`` (and
of `float`/non-``int`` inputs generally) is desired, that would be a
deliberate enhancement to the library, not a bug fix covered by this
suite - flagging it here so the maintainer can decide.
"""

from __future__ import annotations

import pytest

from waxt.calendar_converters import JalaliCalendar

# ---------------------------------------------------------------------------
# jalali_to_gregorian: validated inputs -> ValueError
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "month",
    [0, -1, 13, 14, 100, -100],
    ids=lambda m: f"month={m}",
)
def test_jalali_to_gregorian_rejects_invalid_month(month):
    with pytest.raises(ValueError, match="Invalid Jalali month"):
        JalaliCalendar.jalali_to_gregorian(1403, month, 1)


@pytest.mark.parametrize(
    "j_year, month, day",
    [
        (1403, 1, 0),  # day zero
        (1403, 1, -1),  # negative day
        (1403, 1, 32),  # 31-day month, one day too many
        (1403, 7, 31),  # 30-day month, one day too many
        (1402, 12, 30),  # 30 Esfand in a non-leap year (1402 is non-leap)
        (1400, 12, 30),  # 30 Esfand in a non-leap year (1400 is non-leap)
        (1403, 12, 31),  # Esfand never has 31 days, even in a leap year
    ],
    ids=[
        "day=0",
        "day=-1",
        "31-day-month day=32",
        "30-day-month day=31",
        "30-Esfand-non-leap-1402",
        "30-Esfand-non-leap-1400",
        "31-Esfand-leap-1403",
    ],
)
def test_jalali_to_gregorian_rejects_invalid_day(j_year, month, day):
    with pytest.raises(ValueError, match="Invalid Jalali day"):
        JalaliCalendar.jalali_to_gregorian(j_year, month, day)


def test_jalali_to_gregorian_accepts_30_esfand_in_leap_year():
    # Sanity check companion to the invalid-day tests above: 1403 IS leap.
    assert JalaliCalendar.jalali_to_gregorian(1403, 12, 30) == (2025, 3, 20)


# ---------------------------------------------------------------------------
# jalali_to_gregorian: invalid types -> TypeError
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bad_year", [None, "1403", [1403], {1403}, object()])
def test_jalali_to_gregorian_rejects_non_numeric_year(bad_year):
    with pytest.raises(TypeError):
        JalaliCalendar.jalali_to_gregorian(bad_year, 1, 1)


@pytest.mark.parametrize("bad_month", [None, "1", [1], object()])
def test_jalali_to_gregorian_rejects_non_numeric_month(bad_month):
    with pytest.raises(TypeError):
        JalaliCalendar.jalali_to_gregorian(1403, bad_month, 1)


@pytest.mark.parametrize("bad_day", [None, "1", [1], object()])
def test_jalali_to_gregorian_rejects_non_numeric_day(bad_day):
    with pytest.raises(TypeError):
        JalaliCalendar.jalali_to_gregorian(1403, 1, bad_day)


# ---------------------------------------------------------------------------
# gregorian_to_jalali: invalid types -> TypeError only for the year
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bad_year", [None, "2024", [2024], object()])
def test_gregorian_to_jalali_rejects_non_numeric_year(bad_year):
    with pytest.raises(TypeError):
        JalaliCalendar.gregorian_to_jalali(bad_year, 1, 1)


@pytest.mark.parametrize("bad_month", [None, "1", [1], object()])
def test_gregorian_to_jalali_rejects_non_numeric_month(bad_month):
    with pytest.raises(TypeError):
        JalaliCalendar.gregorian_to_jalali(2024, bad_month, 1)


@pytest.mark.parametrize("bad_day", [None, "1", [1], object()])
def test_gregorian_to_jalali_rejects_non_numeric_day(bad_day):
    with pytest.raises(TypeError):
        JalaliCalendar.gregorian_to_jalali(2024, 1, bad_day)


# ---------------------------------------------------------------------------
# gregorian_to_jalali: documents the *lack* of calendar-range validation.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "g_year, g_month, g_day",
    [
        (2024, 13, 1),  # month 13
        (2024, 0, 1),  # month 0
        (2024, 1, 0),  # day 0
        (2024, 1, 32),  # day 32 in January
        (2024, 2, 30),  # "Feb 30"
        (2023, 2, 30),  # "Feb 30" in a non-leap year too
        (2024, 4, 31),  # "Apr 31"
    ],
    ids=[
        "month=13",
        "month=0",
        "day=0",
        "day=32",
        "feb-30-leap-year",
        "feb-30-non-leap-year",
        "apr-31",
    ],
)
def test_gregorian_to_jalali_does_not_validate_calendar_ranges(g_year, g_month, g_day):
    """`gregorian_to_jalali` has no range validation: it does not raise for
    calendar-invalid Gregorian dates. This test documents that current
    behaviour explicitly, so it fails loudly (as a signal, not a silent
    regression) if validation is ever added."""
    result = JalaliCalendar.gregorian_to_jalali(g_year, g_month, g_day)
    assert isinstance(result, tuple)
    assert len(result) == 3


def test_gregorian_to_jalali_silently_accepts_float_inputs():
    """Floats are not rejected either; they flow straight into arithmetic
    and can produce float-valued (not int-valued) results."""
    result = JalaliCalendar.gregorian_to_jalali(2024.0, 3.0, 20.0)
    assert result == (1403, 1, 1) or all(isinstance(v, float) for v in result)


def test_is_leap_rejects_non_numeric_year():
    with pytest.raises(TypeError):
        JalaliCalendar.is_leap(None)

    with pytest.raises(TypeError):
        JalaliCalendar.is_leap("1403")
