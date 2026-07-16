"""Known-case tests for ``HijriCalendar`` (requirement #1).

IMPORTANT - assumption about calendar type
-------------------------------------------
``HijriCalendar`` implements a **tabular/arithmetic** Islamic calendar
(epoch-based, deterministic leap rule), *not* the observation-based
Umm al-Qura calendar used by Saudi Arabia (and by third-party packages such
as ``hijri-converter``/``hijridate``). This was confirmed by reading the
implementation:

* Epoch: ``HijriCalendar.EPOCH_GREGORIAN_*`` == 622-07-19 (proleptic
  Gregorian), which is the standard "civil" tabular-calendar epoch (Julian
  Day Number 1948440).
* Leap rule: ``(11 * h_year + 25) % 30 < 11`` - a fixed 30-year cycle with
  11 leap years, applied uniformly to every year, with no reference to
  real astronomical new moons.

Because of this, the values pinned below are **not** claims about
real-world/observed Hijri dates (which can differ from the tabular
calendar by a day or two around any given month, since real Hijri months
depend on moon-sighting or the Umm al-Qura tables). They are:

1. The one universally-cited, unambiguous fact about this specific
   calendar family: the epoch equivalence 1 Muharram AH 1 == 19 July 622 CE.
2. Otherwise self-consistent, library-computed reference points (spanning
   AH 1 through AH 1500), pinned here as regression values so that any
   future change to the algorithm's arithmetic is caught explicitly.
"""

from __future__ import annotations

import pytest

from waxt.calendar_converters import HijriCalendar

# (hijri_year, hijri_month, hijri_day,
#  gregorian_year, gregorian_month, gregorian_day, description)
KNOWN_PAIRS = [
    (1, 1, 1, 622, 7, 19, "Hijri epoch: 1 Muharram AH 1"),
    (1, 1, 2, 622, 7, 20, "2 Muharram AH 1"),
    (1, 12, 30, 623, 7, 8, "last day of AH 1 (leap year, 30 Dhu al-Hijjah)"),
    (2, 1, 1, 623, 7, 9, "1 Muharram AH 2 (right after AH 1's leap day)"),
    (2, 12, 29, 624, 6, 26, "last day of AH 2 (non-leap, 29 Dhu al-Hijjah)"),
    (10, 1, 1, 631, 4, 13, "1 Muharram AH 10"),
    (10, 12, 29, 632, 3, 31, "last day of AH 10 (non-leap)"),
    (100, 1, 1, 718, 8, 8, "1 Muharram AH 100"),
    (500, 1, 1, 1106, 9, 9, "1 Muharram AH 500"),
    (500, 12, 30, 1107, 8, 29, "last day of AH 500 (leap year)"),
    (1000, 1, 1, 1591, 10, 20, "1 Muharram AH 1000"),
    (1300, 1, 1, 1882, 11, 13, "1 Muharram AH 1300"),
    (1400, 1, 1, 1979, 11, 21, "1 Muharram AH 1400"),
    (1400, 12, 30, 1980, 11, 9, "last day of AH 1400 (leap year)"),
    (1445, 1, 1, 2023, 7, 20, "1 Muharram AH 1445"),
    (1445, 9, 1, 2024, 3, 12, "1 Ramadan AH 1445"),
    (1445, 12, 29, 2024, 7, 7, "last day of AH 1445 (non-leap)"),
    (1446, 1, 1, 2024, 7, 8, "1 Muharram AH 1446"),
    (1446, 12, 30, 2025, 6, 27, "last day of AH 1446 (leap year)"),
    (1447, 1, 1, 2025, 6, 28, "1 Muharram AH 1447"),
    (1500, 1, 1, 2076, 11, 28, "1 Muharram AH 1500"),
]


@pytest.mark.parametrize(
    "h_year, h_month, h_day, g_year, g_month, g_day, description",
    KNOWN_PAIRS,
    ids=[p[-1] for p in KNOWN_PAIRS],
)
def test_hijri_to_gregorian_known_cases(
    h_year, h_month, h_day, g_year, g_month, g_day, description
):
    assert HijriCalendar.hijri_to_gregorian(h_year, h_month, h_day) == (
        g_year,
        g_month,
        g_day,
    )


@pytest.mark.parametrize(
    "h_year, h_month, h_day, g_year, g_month, g_day, description",
    KNOWN_PAIRS,
    ids=[p[-1] for p in KNOWN_PAIRS],
)
def test_gregorian_to_hijri_known_cases(
    h_year, h_month, h_day, g_year, g_month, g_day, description
):
    assert HijriCalendar.gregorian_to_hijri(g_year, g_month, g_day) == (
        h_year,
        h_month,
        h_day,
    )


def test_epoch_is_the_well_known_civil_tabular_calendar_epoch():
    """1 Muharram AH 1 corresponds to Julian Day Number 1948440, the
    "civil" (Friday-epoch) tabular Islamic calendar epoch used by many
    arithmetic Hijri implementations. This anchors the whole calendar."""
    assert HijriCalendar.hijri_to_gregorian(1, 1, 1) == (622, 7, 19)
    assert HijriCalendar.gregorian_to_hijri(622, 7, 19) == (1, 1, 1)
