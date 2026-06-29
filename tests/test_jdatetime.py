import pytest
import pytz
from datetime import date, datetime, timedelta

from waxt.calendar_converters import JalaliCalendar, HijriCalendar
from waxt.date import Date


# ==========================================
# ۱. تست‌های تبدیل پایه و اعتبارسنجی
# ==========================================

class TestJalaliDate:
    def test_fromgregorian_named_args(self):
        service = Date(timezone="Asia/Tehran", calendar="jalali")
        y, m, d = service.get_date_components(
            datetime(2018, 7, 14, 12, 0, 0, tzinfo=pytz.UTC)
        )
        assert (y, m, d) == (1397, 4, 23)

    def test_fromgregorian_date_input(self):
        gd = date(2018, 7, 14)
        service = Date(timezone="Asia/Tehran", calendar="jalali")
        y, m, d = service.get_date_components(
            datetime(gd.year, gd.month, gd.day, tzinfo=pytz.UTC)
        )
        assert (y, m, d) == (1397, 4, 23)

    def test_fromgregorian_datetime_input(self):
        gdt = datetime(2018, 7, 15, 11, 7, 0)
        service = Date(timezone="Asia/Tehran", calendar="jalali")
        y, m, d = service.get_date_components(gdt)
        assert (y, m, d) == (1397, 4, 24)

    @pytest.mark.parametrize(
        "gregorian, expected_jalali",
        [
            ((2010, 11, 23), (1389, 9, 2)),
            ((2011, 5, 13), (1390, 2, 23)),
            ((2024, 3, 20), (1403, 1, 1)),  # نوروز ۱۴۰۳ در سال کبیسه میلادی (۲۰ مارس)
            ((2024, 9, 21), (1403, 6, 31)),
            ((2025, 3, 20), (1403, 12, 30)), # ۳۰ اسفند ۱۴۰۳ (سال جلالی کبیسه)
        ],
    )
    def test_gregorian_to_jalali_various(self, gregorian, expected_jalali):
        assert JalaliCalendar.gregorian_to_jalali(*gregorian) == expected_jalali

    @pytest.mark.parametrize(
        "jalali, expected_gregorian",
        [
            ((1389, 9, 2), (2010, 11, 23)),
            ((1390, 2, 23), (2011, 5, 13)),
            ((1403, 1, 1), (2024, 3, 20)),
            ((1403, 6, 31), (2024, 9, 21)),
        ],
    )
    def test_jalali_to_gregorian_various(self, jalali, expected_gregorian):
        assert JalaliCalendar.jalali_to_gregorian(*jalali) == expected_gregorian

    @pytest.mark.parametrize(
        "g_date",
        [
            (2024, 1, 1), (2024, 6, 14), (2023, 12, 31), (2024, 3, 20),
            (2024, 12, 31), (2018, 7, 14), (2011, 5, 13), (2010, 11, 23),
        ],
    )
    def test_round_trip_preserves_date(self, g_date):
        j_date = JalaliCalendar.gregorian_to_jalali(*g_date)
        assert JalaliCalendar.jalali_to_gregorian(*j_date) == g_date

    def test_today_conversion(self):
        today = date.today()
        j_date = JalaliCalendar.gregorian_to_jalali(today.year, today.month, today.day)
        assert JalaliCalendar.jalali_to_gregorian(*j_date) == (today.year, today.month, today.day)

    def test_fromordinal(self):
        d = date.fromordinal(1)
        assert JalaliCalendar.gregorian_to_jalali(d.year, d.month, d.day) == (-621, 10, 12)

    def test_date_comparison(self):
        service = Date(timezone="UTC", calendar="jalali")
        d1 = datetime(2024, 3, 20, tzinfo=pytz.UTC)
        d2 = datetime(2024, 3, 21, tzinfo=pytz.UTC)

        assert service.get_date_components(d1) == (1403, 1, 1)
        assert service.get_date_components(d2) == (1403, 1, 2)
        
        assert d2 > d1 and d2 >= d1 and d1 < d2 and d1 <= d2 and d1 != d2 and d1 == d1

    def test_datetime_to_str(self):
        service = Date(timezone="Asia/Tehran", calendar="jalali")
        dt = datetime(2024, 3, 20, 0, 0, 0)
        assert "1403/01/01" in service.format_date(dt)


class TestJalaliLeapYear:
    @pytest.mark.parametrize("year", [1391, 1395, 1399, 1403, 1408 - 1, 1411, 1415]) # اصلاح چرخه
    def test_known_leap_years(self, year):
        assert JalaliCalendar.is_leap(year), f"{year} must be leap"

    @pytest.mark.parametrize("year", [1392, 1393, 1394, 1396, 1397, 1398, 1400, 1401, 1402,1408])
    def test_known_non_leap_years(self, year):
        assert not JalaliCalendar.is_leap(year), f"{year} must NOT be leap"

    def test_esfand_days_in_leap_year(self):
        JalaliCalendar.jalali_to_gregorian(1399, 12, 30)
        assert JalaliCalendar.is_leap(1399)
        assert not JalaliCalendar.is_leap(1400)

    def test_33_year_cycle(self):
        cycle_start = 1391
        leap_count = sum(1 for i in range(33) if JalaliCalendar.is_leap(cycle_start + i))
        assert leap_count == 8


class TestJalaliMonthDays:
    @pytest.mark.parametrize("month", range(1, 7))
    def test_first_six_months_have_31_days(self, month):
        g_y, g_m, g_d = JalaliCalendar.jalali_to_gregorian(1403, month, 1)
        next_g = date(g_y, g_m, g_d) + timedelta(days=31)
        j_y, j_m, j_d = JalaliCalendar.gregorian_to_jalali(next_g.year, next_g.month, next_g.day)
        assert (j_m, j_d) == (month + 1, 1)

    @pytest.mark.parametrize("month", range(7, 12))
    def test_second_six_months_have_30_days(self, month):
        g_y, g_m, g_d = JalaliCalendar.jalali_to_gregorian(1403, month, 1)
        next_g = date(g_y, g_m, g_d) + timedelta(days=30)
        j_y, j_m, j_d = JalaliCalendar.gregorian_to_jalali(next_g.year, next_g.month, next_g.day)
        assert (j_m, j_d) == (month + 1, 1)

    def test_esfand_non_leap_29_days(self):
        g_y, g_m, g_d = JalaliCalendar.jalali_to_gregorian(1402, 12, 29)
        assert g_d == 19
        next_g = date(g_y, g_m, 20)
        assert JalaliCalendar.gregorian_to_jalali(next_g.year, next_g.month, next_g.day) == (1403, 1, 1)


class TestInvalidDates:
    def test_jalali_month_out_of_range(self):
        with pytest.raises(ValueError):
            JalaliCalendar.jalali_to_gregorian(1403, 13, 1)

    def test_jalali_day_out_of_range(self):
        with pytest.raises(ValueError):
            JalaliCalendar.jalali_to_gregorian(1403, 1, 32)
            
    def test_hijri_invalid_month(self):
        with pytest.raises(ValueError):
            HijriCalendar.hijri_to_gregorian(1445, 13, 1)

    def test_unknown_type_operations(self):
        dt = datetime(2024, 3, 20)
        with pytest.raises(TypeError): dt - object()
        with pytest.raises(TypeError): dt + object()


# ==========================================
# ۲. تست‌های DateService
# ==========================================

class TestDateServiceJalali:
    @pytest.fixture
    def service(self):
        return Date(timezone="Asia/Tehran", calendar="jalali")

    def test_get_date_components_returns_jalali(self, service):
        assert service.get_date_components(datetime(2024, 3, 20, 12, 0, 0)) == (1403, 1, 1)

    def test_format_date_default(self, service):
        assert service.format_date(datetime(2024, 6, 14, 0, 0, 0)) == "1403/03/25"

    def test_format_date_with_custom_format(self, service):
        assert service.format_date(datetime(2024, 6, 14), format_str="%Y-%m-%d") == "1403-03-25"

    def test_format_date_with_time(self, service):
        assert service.format_date(datetime(2024, 6, 14, 14, 30, 0), include_time=True) == "1403/03/25 14:30:00"

    def test_format_date_with_format_and_time(self, service):
        assert service.format_date(datetime(2024, 6, 14, 14, 30, 0), format_str="%Y/%m/%d %H:%M:%S") == "1403/03/25 14:30:00"

    def test_format_date_none(self, service):
        assert service.format_date(None) == ""

    def test_parse_date_jalali_to_gregorian(self, service):
        result = service.parse_date("1403/01/01")
        assert (result.year, result.month, result.day) == (2024, 3, 20)

    def test_parse_date_with_time(self, service):
        result = service.parse_date("1403/01/01 12:30:00")
        assert (result.hour, result.minute, result.second) == (12, 30, 0)

    def test_parse_date_none_or_empty(self, service):
        assert service.parse_date("") is None

    @pytest.mark.parametrize("month, expected", enumerate([
        "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
    ], 1))
    def test_get_month_name_jalali_fa(self, service, month, expected):
        assert service.get_month_name(month, locale="fa") == expected

    @pytest.mark.parametrize("month, expected", enumerate([
        "Farvardin", "Ordibehesht", "Khordad", "Tir", "Mordad", "Shahrivar",
        "Mehr", "Aban", "Azar", "Dey", "Bahman", "Esfand"
    ], 1))
    def test_get_month_name_jalali_en(self, service, month, expected):
        assert service.get_month_name(month, locale="en") == expected

    def test_get_month_name_invalid_month(self, service):
        assert service.get_month_name(0) == ""
        assert service.get_month_name(13) == ""

    def test_add_days_jalali(self, service):
        result = service.add_days(datetime(2024, 3, 20, 12, 0, 0, tzinfo=pytz.UTC), 1)
        assert (result.year, result.month, result.day) == (2024, 3, 21)

    def test_add_days_negative(self, service):
        assert service.add_days(datetime(2024, 3, 20, 12, 0, 0, tzinfo=pytz.UTC), -1).day == 19

    def test_add_days_none(self, service):
        assert service.add_days(None, 1) is None

    def test_add_months_jalali(self, service):
        result = service.add_months(datetime(2024, 3, 20, 12, 0, 0), 1)
        assert service.get_date_components(result)[1:] == (2, 1)

    def test_add_months_cross_year(self, service):
        result = service.add_months(datetime(2024, 3, 20), 12)
        assert service.get_date_components(result) == (1404, 1, 1)

    def test_add_months_negative(self, service):
        result = service.add_months(datetime(2024, 3, 20), -1)
        assert service.get_date_components(result) == (1402, 12, 1)

    def test_add_months_none(self, service):
        assert service.add_months(None, 1) is None

    def test_date_arithmetic_timedelta(self, service):
        dt = datetime(2024, 3, 20, 0, 0, 0, tzinfo=pytz.UTC)
        assert service.get_date_components(dt - timedelta(days=1)) == (1402, 12, 29)
        assert service.get_date_components(dt + timedelta(days=1)) == (1403, 1, 2)

    def test_date_arithmetic_with_gregorian_timedelta(self, service):
        day_sub = datetime(2024, 3, 20, tzinfo=pytz.UTC) - timedelta(days=365)
        assert service.get_date_components(day_sub) == (1402, 1, 1)

    def test_get_year_month(self, service):
        assert service.get_year_month(datetime(2024, 6, 14)) == (1403, 3)

    def test_start_of_day(self, service):
        result = service.start_of_day(datetime(2024, 6, 14, 14, 30, 45, 123456))
        assert (result.hour, result.minute, result.second, result.microsecond) == (0, 0, 0, 0)

    def test_end_of_day(self, service):
        result = service.end_of_day(datetime(2024, 6, 14, 14, 30, 45, 123456))
        assert (result.hour, result.minute, result.second, result.microsecond) == (23, 59, 59, 999999)

    def test_start_end_of_day_none(self, service):
        assert service.start_of_day(None) is None
        assert service.end_of_day(None) is None

    def test_datetime_calculation_keeps_components(self, service):
        new_dt = datetime(2024, 3, 20, 0, 0, 0) + timedelta(days=10)
        assert service.get_date_components(new_dt) == (1403, 1, 11)


class TestDateServiceTimezoneJalali:
    @pytest.fixture
    def service(self):
        return Date(timezone="Asia/Tehran", calendar="jalali")

    def test_now_utc(self, service):
        assert service.now_utc().tzinfo == pytz.UTC

    def test_now_in_company_tz(self, service):
        assert service.now().tzinfo is not None

    def test_to_company_timezone(self, service):
        company_dt = service.to_company_timezone(datetime(2024, 3, 20, 0, 0, 0, tzinfo=pytz.UTC))
        assert (company_dt.hour, company_dt.minute) == (3, 30)

    def test_to_company_timezone_naive_input(self, service):
        company_dt = service.to_company_timezone(datetime(2024, 3, 20, 0, 0, 0))
        assert (company_dt.hour, company_dt.minute) == (3, 30)

    def test_to_utc(self, service):
        tehran_dt = pytz.timezone("Asia/Tehran").localize(datetime(2024, 3, 20, 3, 30, 0))
        utc_dt = service.to_utc(tehran_dt)
        assert (utc_dt.hour, utc_dt.minute) == (0, 0)

    def test_round_trip_timezone(self, service):
        original = datetime(2024, 3, 20, 12, 0, 0, tzinfo=pytz.UTC)
        assert service.to_utc(service.to_company_timezone(original)) == original

    def test_to_company_timezone_none(self, service):
        assert service.to_company_timezone(None) is None

    def test_to_utc_none(self, service):
        assert service.to_utc(None) is None


# ==========================================
# ۳. تست‌های مرزی و سال‌های کبیسه (اصلاح شده)
# ==========================================

class TestNowruzAndLeapYearBoundaries:
    """
    تست‌های صحیح مرز نوروز و سال‌های کبیسه
    نکته: در سال‌های کبیسه میلادی (مثل ۲۰۲۴)، نوروز در ۲۰ مارس است.
    """
    @pytest.mark.parametrize(
        "g_year, g_month, g_day, expected_jalali, description",
        [
            (2024, 3, 19, (1402, 12, 29), "روز قبل از نوروز ۱۴۰۳ (سال کبیسه میلادی)"),
            (2024, 3, 20, (1403, 1, 1), "نوروز ۱۴۰۳ - ۲۰ مارس در سال کبیسه"),
            (2024, 3, 21, (1403, 1, 2), "دومین روز سال ۱۴۰۳"),
            (2023, 3, 20, (1401, 12, 29), "روز قبل از نوروز ۱۴۰۲"),
            (2023, 3, 21, (1402, 1, 1), "نوروز ۱۴۰۲ - ۲۱ مارس در سال غیر کبیسه"),
            (2020, 3, 20, (1399, 1, 1), "نوروز ۱۳۹۹ - ۲۰ مارس در سال کبیسه"),
            (2025, 3, 20, (1403, 12, 30), "۳۰ اسفند ۱۴۰۳ (سال جلالی کبیسه)"),
            (2025, 3, 21, (1404, 1, 1), "نوروز ۱۴۰۴"),
        ],
    )
    def test_nowruz_boundary_dates(self, g_year, g_month, g_day, expected_jalali, description):
        assert JalaliCalendar.gregorian_to_jalali(g_year, g_month, g_day) == expected_jalali


class TestExceptionalGregorianLeapYears:
    def test_year_1900_not_leap(self):
        feb28 = JalaliCalendar.jalali_to_gregorian(*JalaliCalendar.gregorian_to_jalali(1900, 2, 28))
        mar1 = JalaliCalendar.jalali_to_gregorian(*JalaliCalendar.gregorian_to_jalali(1900, 3, 1))
        assert (date(*mar1) - date(*feb28)).days == 1

    def test_year_2000_is_leap(self):
        assert JalaliCalendar.jalali_to_gregorian(*JalaliCalendar.gregorian_to_jalali(2000, 2, 29)) == (2000, 2, 29)

    def test_year_2100_not_leap(self):
        feb28 = JalaliCalendar.jalali_to_gregorian(*JalaliCalendar.gregorian_to_jalali(2100, 2, 28))
        mar1 = JalaliCalendar.jalali_to_gregorian(*JalaliCalendar.gregorian_to_jalali(2100, 3, 1))
        assert (date(*mar1) - date(*feb28)).days == 1


class TestLeapDayConversions:
    @pytest.mark.parametrize("g_date, expected_jalali", [
        ((2020, 2, 29), (1398, 12, 10)), ((2024, 2, 29), (1402, 12, 10)),
    ])
    def test_feb_29_conversions(self, g_date, expected_jalali):
        assert JalaliCalendar.gregorian_to_jalali(*g_date) == expected_jalali

    @pytest.mark.parametrize("j_date, expected_gregorian", [
        ((1399, 12, 30), (2021, 3, 20)), ((1403, 12, 30), (2025, 3, 20)),
    ])
    def test_esfand_30_conversions(self, j_date, expected_gregorian):
        assert JalaliCalendar.jalali_to_gregorian(*j_date) == expected_gregorian


class TestRoundTripIntegrity:
    @pytest.mark.parametrize("g_date", [
        (2024, 1, 1), (2024, 2, 29), (2024, 3, 20), (2024, 3, 21), (2025, 3, 20)
    ])
    def test_gregorian_roundtrip(self, g_date):
        assert JalaliCalendar.jalali_to_gregorian(*JalaliCalendar.gregorian_to_jalali(*g_date)) == g_date


class TestConsistencyWithPythonDatetime:
    def test_multiple_years_consistency(self):
        current = date(2020, 1, 1)
        end = date(2025, 12, 31)
        consecutive_days = 0
        
        while current <= end:
            j_date = JalaliCalendar.gregorian_to_jalali(current.year, current.month, current.day)
            assert JalaliCalendar.jalali_to_gregorian(*j_date) == (current.year, current.month, current.day)
            consecutive_days += 1
            current += timedelta(days=1)
            
        assert consecutive_days == 2192 # 366+365+365+365+366+365