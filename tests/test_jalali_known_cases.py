"""Known-case tests for ``JalaliCalendar`` (requirement #1).

Every pair below was cross-verified against the ``jdatetime`` package (a
well established third-party Jalali calendar implementation) at the time
this suite was written, so they double as an independent sanity check, not
just numbers pulled out of thin air.
"""

from __future__ import annotations

import pytest

from waxt.calendar_converters import JalaliCalendar

# (gregorian_year, gregorian_month, gregorian_day,
#  jalali_year, jalali_month, jalali_day, description)
KNOWN_PAIRS = [
    (1921, 3, 21, 1300, 1, 1, "Nowruz 1300"),
    (1922, 3, 20, 1300, 12, 29, "last day of 1300 (non-leap)"),
    (1946, 3, 21, 1325, 1, 1, "Nowruz 1325"),
    (1969, 7, 20, 1348, 4, 29, "Apollo 11 Moon landing"),
    (1971, 3, 21, 1350, 1, 1, "Nowruz 1350"),
    (1978, 1, 1, 1356, 10, 11, "New Year's Day 1978"),
    (1979, 2, 11, 1357, 11, 22, "Iranian Revolution victory day (22 Bahman)"),
    (1980, 9, 22, 1359, 6, 31, "Start of the Iran-Iraq war (31 Shahrivar)"),
    (1988, 3, 21, 1367, 1, 1, "Nowruz 1367"),
    (1991, 3, 21, 1370, 1, 1, "Nowruz 1370"),
    (1993, 3, 21, 1372, 1, 1, "Nowruz 1372"),
    (1997, 3, 21, 1376, 1, 1, "Nowruz 1376"),
    (2000, 1, 1, 1378, 10, 11, "Y2K"),
    (2001, 3, 21, 1380, 1, 1, "Nowruz 1380"),
    (2001, 9, 11, 1380, 6, 20, "September 11 attacks"),
    (2011, 3, 21, 1390, 1, 1, "Nowruz 1390"),
    (2016, 3, 20, 1395, 1, 1, "Nowruz 1395"),
    (2017, 3, 21, 1396, 1, 1, "Nowruz 1396"),
    (2019, 3, 21, 1398, 1, 1, "Nowruz 1398"),
    (2020, 3, 20, 1399, 1, 1, "Nowruz 1399"),
    (2021, 3, 21, 1400, 1, 1, "Nowruz 1400"),
    (2022, 3, 21, 1401, 1, 1, "Nowruz 1401"),
    (2023, 3, 21, 1402, 1, 1, "Nowruz 1402"),
    (2024, 3, 19, 1402, 12, 29, "last day of 1402 (non-leap)"),
    (2024, 3, 20, 1403, 1, 1, "Nowruz 1403 (the leap-year-debate year)"),
    (2024, 3, 21, 1403, 1, 2, "2 Farvardin 1403"),
    (2025, 3, 20, 1403, 12, 30, "last day of 1403 (leap, 30 days in Esfand)"),
    (2025, 3, 21, 1404, 1, 1, "Nowruz 1404"),
    (2026, 3, 21, 1405, 1, 1, "Nowruz 1405"),
    (1900, 1, 1, 1278, 10, 11, "start of the 20th century"),
    (1600, 1, 1, 978, 10, 11, "start of the required support range"),
    (2500, 12, 31, 1879, 10, 10, "end of the required support range"),
]


@pytest.mark.parametrize(
    "g_year, g_month, g_day, j_year, j_month, j_day, description",
    KNOWN_PAIRS,
    ids=[p[-1] or f"{p[0]}-{p[1]}-{p[2]}" for p in KNOWN_PAIRS],
)
def test_gregorian_to_jalali_known_cases(
    g_year, g_month, g_day, j_year, j_month, j_day, description
):
    assert JalaliCalendar.gregorian_to_jalali(g_year, g_month, g_day) == (
        j_year,
        j_month,
        j_day,
    )


@pytest.mark.parametrize(
    "g_year, g_month, g_day, j_year, j_month, j_day, description",
    KNOWN_PAIRS,
    ids=[p[-1] or f"{p[3]}-{p[4]}-{p[5]}" for p in KNOWN_PAIRS],
)
def test_jalali_to_gregorian_known_cases(
    g_year, g_month, g_day, j_year, j_month, j_day, description
):
    assert JalaliCalendar.jalali_to_gregorian(j_year, j_month, j_day) == (
        g_year,
        g_month,
        g_day,
    )
