from datetime import datetime, timedelta, timezone

import pytest

from waxt import country, tzinfo
from waxt.timezone import COUNTRIES, CountryTimezone, Timezone


def test_country_metadata_is_bundled() -> None:
    iran = country("ir")

    assert isinstance(iran, CountryTimezone)
    assert iran.code == "IR"
    assert iran.name == "Iran, Islamic Republic of"
    assert iran.timezone == "Asia/Tehran"
    assert iran.offset == 210
    assert iran.week == 6
    assert iran.calendar == "persian"
    assert iran.rtl is True
    assert len(COUNTRIES) > 200


def test_country_calendars_use_territory_preferences() -> None:
    non_gregorian = {
        code: metadata.calendar
        for code, metadata in COUNTRIES.items()
        if metadata.calendar != "gregorian"
    }

    assert non_gregorian == {
        "AF": "persian",
        "IR": "persian",
        "TH": "buddhist",
    }


def test_country_text_direction_uses_dominant_written_locale() -> None:
    rtl_countries = {code for code, metadata in COUNTRIES.items() if metadata.rtl}

    assert rtl_countries == {
        "AE",
        "AF",
        "BH",
        "CC",
        "DZ",
        "EG",
        "IL",
        "IQ",
        "IR",
        "JO",
        "KM",
        "KW",
        "LB",
        "LY",
        "MA",
        "MR",
        "MV",
        "OM",
        "PK",
        "PS",
        "QA",
        "SA",
        "SD",
        "SY",
        "TN",
        "YE",
    }


def test_country_code_is_normalized() -> None:
    assert country(" gb ") is COUNTRIES["GB"]


def test_tzinfo_returns_cached_custom_timezone() -> None:
    zone = tzinfo("US")

    assert zone is tzinfo("US")
    assert zone.zone == "America/Adak"
    assert isinstance(zone, Timezone)
    assert zone.utcoffset(None) == timedelta(hours=-10)
    assert zone.dst(None) == timedelta(0)


def test_tzinfo_works_with_standard_datetime() -> None:
    tehran = tzinfo("IR")
    local = datetime(2025, 1, 15, 12, tzinfo=tehran)

    assert local.utcoffset() == timedelta(hours=3, minutes=30)
    assert local.tzname() == "Asia/Tehran"
    assert local.astimezone(timezone.utc) == datetime(
        2025, 1, 15, 8, 30, tzinfo=timezone.utc
    )


def test_tzinfo_applies_daylight_saving_rules() -> None:
    adak = tzinfo("US")
    winter = datetime(2025, 1, 15, 12, tzinfo=adak)
    summer = datetime(2025, 7, 15, 12, tzinfo=adak)

    assert winter.utcoffset() == timedelta(hours=-10)
    assert winter.dst() == timedelta(0)
    assert summer.utcoffset() == timedelta(hours=-9)
    assert summer.dst() == timedelta(hours=1)


def test_tzinfo_converts_across_daylight_saving_transition() -> None:
    adak = tzinfo("US")

    before = datetime(2025, 3, 9, 11, 59, tzinfo=timezone.utc).astimezone(adak)
    after = datetime(2025, 3, 9, 12, tzinfo=timezone.utc).astimezone(adak)

    assert before.replace(tzinfo=None) == datetime(2025, 3, 9, 1, 59)
    assert before.utcoffset() == timedelta(hours=-10)
    assert after.replace(tzinfo=None) == datetime(2025, 3, 9, 3)
    assert after.utcoffset() == timedelta(hours=-9)


@pytest.mark.parametrize("code", ["", "USA", "ZZ"])
def test_invalid_country_code(code: str) -> None:
    with pytest.raises(ValueError):
        tzinfo(code)


def test_non_string_country_code() -> None:
    with pytest.raises(TypeError):
        country(123)  # type: ignore[arg-type]
