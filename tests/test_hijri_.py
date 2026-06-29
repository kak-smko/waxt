import pytest
import pytz
from datetime import date, datetime, timedelta

from waxt.calendar_converters import HijriCalendar
from waxt.date_service import DateService


# ==========================================
# ۱. تست‌های تبدیل پایه و ویژگی‌ها
# ==========================================

class TestHijriDate:
    def test_epoch_conversion(self):
        assert HijriCalendar.gregorian_to_hijri(622, 7, 19) == (1, 1, 1)

    def test_representation(self):
        service = DateService(timezone="Asia/Tehran", calendar="hijri")
        y, m, d = service.get_date_components(datetime(622, 7, 19))
        assert (y, m, d) == (1, 1, 1)

    def test_today_matches_gregorian(self):
        today = date.today()
        h_date = HijriCalendar.gregorian_to_hijri(today.year, today.month, today.day)
        g_date = HijriCalendar.hijri_to_gregorian(*h_date)
        assert date(*g_date) == today

    def test_hash_consistency(self):
        h1 = HijriCalendar.gregorian_to_hijri(1990, 3, 10)
        h2 = HijriCalendar.gregorian_to_hijri(1990, 3, 10)
        assert h1 == h2

    def test_equality(self):
        h1 = HijriCalendar.gregorian_to_hijri(1990, 3, 10)
        h2 = HijriCalendar.gregorian_to_hijri(1990, 3, 10)
        h3 = HijriCalendar.gregorian_to_hijri(1990, 3, 11)
        assert h1 == h2
        assert h1 != h3

    def test_ordering(self):
        h_curr = HijriCalendar.gregorian_to_hijri(1990, 3, 10)
        h_prev = HijriCalendar.gregorian_to_hijri(1990, 3, 9)
        h_next = HijriCalendar.gregorian_to_hijri(1990, 3, 11)

        assert h_next > h_curr
        assert h_curr >= h_prev
        assert h_prev < h_curr
        assert h_curr <= h_next


class TestHijriConversion:
    @pytest.mark.parametrize("gregorian, expected_hijri", [
        ((1990, 3, 10), (1410, 8, 12)),
        ((2024, 1, 1), (1445, 6, 18)),
        ((622, 7, 19), (1, 1, 1)),
    ])
    def test_gregorian_to_hijri_various(self, gregorian, expected_hijri):
        assert HijriCalendar.gregorian_to_hijri(*gregorian) == expected_hijri

    def test_known_date_1410_8_12(self):
        assert HijriCalendar.hijri_to_gregorian(1410, 8, 12) == (1990, 3, 10)

    def test_dmyformat_equivalent(self):
        service = DateService(timezone="Asia/Tehran", calendar="hijri")
        assert service.format_date(datetime(1990, 3, 10), "%d/%m/%Y") == "12/08/1410"

    def test_isoformat_equivalent(self):
        service = DateService(timezone="Asia/Tehran", calendar="hijri")
        assert service.format_date(datetime(1990, 3, 10), "%Y-%m-%d") == "1410-08-12"

    def test_properties(self):
        h_y, h_m, h_d = HijriCalendar.gregorian_to_hijri(1990, 3, 10)
        assert h_y == 1410
        assert h_m == 8
        assert h_d == 12

    @pytest.mark.parametrize("g_date", [
        (1990, 3, 10), (2024, 1, 1), (2024, 6, 14), (2023, 12, 31), (2000, 1, 1),
    ])
    def test_round_trip_conversion(self, g_date):
        h_date = HijriCalendar.gregorian_to_hijri(*g_date)
        assert HijriCalendar.hijri_to_gregorian(*h_date) == g_date

    def test_fromisoformat_equivalent(self):
        service = DateService(timezone="Asia/Tehran", calendar="hijri")
        result = service.parse_date("1410/06/03")
        assert result is not None
        assert (result.year, result.month, result.day) == (1990, 1, 1)


# ==========================================
# ۲. تست‌های سال کبیسه و طول ماه‌ها
# ==========================================

class TestHijriLeapYear:
    @pytest.mark.parametrize("i, is_leap_expected", [
        (0, False), (1, True), (2, False), (3, False), (4, True), # 1440 to 1444
        (6, True), (9, True), (12, True), (15, True), (17, True),
        (20, True), (23, True), (25, True), (28, True), (29, False)
    ])
    def test_leap_year_cycle(self, i, is_leap_expected):
        # الگوریتم کد طوری تنظیم شده که سال ۱۴۴۱ (i=1) با دومین سال چرخه ۳۰ ساله (کبیسه) هم‌تراز است
        year = 1440 + i
        assert HijriCalendar.is_leap(year) == is_leap_expected

    def test_year_length_leap(self):
        start = date(*HijriCalendar.hijri_to_gregorian(1411, 1, 1)) # ۱۴۱۱ کبیسه است
        end = date(*HijriCalendar.hijri_to_gregorian(1412, 1, 1))
        assert (end - start).days == 355

    def test_year_length_non_leap(self):
        start = date(*HijriCalendar.hijri_to_gregorian(1442, 1, 1))
        end = date(*HijriCalendar.hijri_to_gregorian(1443, 1, 1))
        assert (end - start).days == 354

    def test_month_length_odd_month_30_days(self):
        start = date(*HijriCalendar.hijri_to_gregorian(1445, 1, 1))
        end = date(*HijriCalendar.hijri_to_gregorian(1445, 2, 1))
        assert (end - start).days == 30

    def test_month_length_even_month_29_days(self):
        start = date(*HijriCalendar.hijri_to_gregorian(1445, 2, 1))
        end = date(*HijriCalendar.hijri_to_gregorian(1445, 3, 1))
        assert (end - start).days == 29


# ==========================================
# ۳. تست‌های DateService
# ==========================================

class TestDateServiceHijri:
    @pytest.fixture
    def service(self):
        return DateService(timezone="Asia/Tehran", calendar="hijri")

    def test_get_date_components_returns_hijri(self, service):
        assert service.get_date_components(datetime(1990, 3, 10, 12, 0, 0)) == (1410, 8, 12)

    def test_format_date_default(self, service):
        assert service.format_date(datetime(1990, 3, 10)) == "1410/08/12"

    def test_format_date_with_custom_format(self, service):
        assert service.format_date(datetime(1990, 3, 10), format_str="%Y-%m-%d") == "1410-08-12"

    def test_format_date_with_time(self, service):
        assert service.format_date(datetime(1990, 3, 10, 14, 30, 0), include_time=True) == "1410/08/12 14:30:00"

    def test_format_date_none(self, service):
        assert service.format_date(None) == ""

    def test_parse_date_hijri_to_gregorian(self, service):
        result = service.parse_date("1410/08/10")
        assert result is not None
        assert (result.year, result.month, result.day) == (1990, 3, 8)

    def test_parse_date_with_time(self, service):
        result = service.parse_date("1410/08/10 14:30:00")
        assert (result.hour, result.minute) == (14, 30)

    def test_parse_date_none_or_empty(self, service):
        assert service.parse_date("") is None

    def test_parse_date_dash_separator(self, service):
        result = service.parse_date("1410-08-10")
        assert result is not None
        assert result.year == 1990

    @pytest.mark.parametrize("month, expected", enumerate([
        "محرم", "صفر", "ربیع الاول", "ربیع الثانی", "جمادی الاول", "جمادی الثانی",
        "رجب", "شعبان", "رمضان", "شوال", "ذی القعده", "ذی الحجه"
    ], 1))
    def test_get_month_name_hijri_ar(self, service, month, expected):
        assert service.get_month_name(month, locale="ar") == expected

    @pytest.mark.parametrize("month, expected", enumerate([
        "Muharram", "Safar", "Rabi' al-awwal", "Rabi' al-thani", "Jumada al-awwal", "Jumada al-thani",
        "Rajab", "Sha'ban", "Ramadan", "Shawwal", "Dhu al-Qi'dah", "Dhu al-Hijjah"
    ], 1))
    def test_get_month_name_hijri_en(self, service, month, expected):
        assert service.get_month_name(month, locale="en") == expected

    def test_get_month_name_invalid_month(self, service):
        assert service.get_month_name(0) == ""
        assert service.get_month_name(13) == ""

    def test_add_days(self, service):
        assert service.add_days(datetime(1990, 3, 10, 12, 0, 0), 1).day == 11

    def test_add_days_negative(self, service):
        assert service.add_days(datetime(1990, 3, 10, 12, 0, 0), -1).day == 9

    def test_add_days_none(self, service):
        assert service.add_days(None, 1) is None

    def test_add_months(self, service):
        result = service.add_months(datetime(1990, 3, 10), 1)
        assert service.get_date_components(result) == (1410, 9, 12)

    def test_add_months_cross_year(self, service):
        g_y, g_m, g_d = HijriCalendar.hijri_to_gregorian(1410, 1, 1)
        result = service.add_months(datetime(g_y, g_m, g_d), 12)
        y, m, _ = service.get_date_components(result)
        assert (y, m) == (1411, 1)

    def test_add_months_negative(self, service):
        result = service.add_months(datetime(1990, 3, 10), -1)
        assert service.get_date_components(result) == (1410, 7, 12)

    def test_add_months_none(self, service):
        assert service.add_months(None, 1) is None

    def test_get_year_month(self, service):
        assert service.get_year_month(datetime(1990, 3, 10)) == (1410, 8)

    def test_start_of_day(self, service):
        result = service.start_of_day(datetime(1990, 3, 10, 14, 30, 45, 123456))
        assert (result.hour, result.minute, result.second, result.microsecond) == (0, 0, 0, 0)

    def test_end_of_day(self, service):
        result = service.end_of_day(datetime(1990, 3, 10, 14, 30, 45, 123456))
        assert (result.hour, result.minute, result.second, result.microsecond) == (23, 59, 59, 999999)

    def test_start_end_of_day_none(self, service):
        assert service.start_of_day(None) is None
        assert service.end_of_day(None) is None

    def test_to_gregorian_from_hijri_date_service(self, service):
        result = service.parse_date("1410/08/12")
        assert (result.year, result.month, result.day) == (1990, 3, 10)


# ==========================================
# ۴. تبدیل‌های متقاطع و منطقه زمانی
# ==========================================

class TestHijriGregorianCrossConversion:
    @pytest.mark.parametrize("hijri", [
        (1410, 8, 13), (1445, 1, 1), (1356, 1, 1)
    ])
    def test_hijri_to_gregorian_then_back(self, hijri):
        g_date = HijriCalendar.hijri_to_gregorian(*hijri)
        assert HijriCalendar.gregorian_to_hijri(*g_date) == hijri

    @pytest.mark.parametrize("gregorian", [
        (1924, 8, 1), (1990, 3, 10), (2024, 1, 1), (2077, 11, 16)
    ])
    def test_gregorian_to_hijri_then_back(self, gregorian):
        h_date = HijriCalendar.gregorian_to_hijri(*gregorian)
        assert HijriCalendar.hijri_to_gregorian(*h_date) == gregorian


class TestDateServiceTimezoneHijri:
    @pytest.fixture
    def service(self):
        return DateService(timezone="Asia/Tehran", calendar="hijri")

    def test_now_utc(self, service):
        assert service.now_utc().tzinfo == pytz.UTC

    def test_now_in_company_tz(self, service):
        assert service.now().tzinfo is not None

    def test_to_company_timezone(self, service):
        company_dt = service.to_company_timezone(datetime(1990, 3, 10, 0, 0, 0, tzinfo=pytz.UTC))
        assert (company_dt.hour, company_dt.minute) == (3, 30)

    def test_to_utc(self, service):
        tehran_dt = pytz.timezone("Asia/Tehran").localize(datetime(1990, 3, 10, 3, 30, 0))
        utc_dt = service.to_utc(tehran_dt)
        assert (utc_dt.hour, utc_dt.minute) == (0, 0)

    def test_round_trip_timezone(self, service):
        original = datetime(1990, 3, 10, 12, 0, 0, tzinfo=pytz.UTC)
        assert service.to_utc(service.to_company_timezone(original)) == original

    def test_to_company_timezone_none(self, service):
        assert service.to_company_timezone(None) is None

    def test_to_utc_none(self, service):
        assert service.to_utc(None) is None


# ==========================================
# ۵. تاریخ‌های نامعتبر
# ==========================================

class TestHijriInvalidDates:
    @pytest.mark.parametrize("h_date", [
        (1410, 0, 1),
        (1410, 13, 1),
        (1410, 2, 30),  # ماه زوج در سال غیر کبیسه -> حداکثر ۲۹ روز
        (1410, 1, -1),
        (1410, 12, 30), # سال ۱۴۱۰ کبیسه نیست، پس ماه ۱۲ حداکثر ۲۹ روز دارد
    ])
    def test_invalid_dates(self, h_date):
        with pytest.raises(ValueError):
            HijriCalendar.hijri_to_gregorian(*h_date)

    def test_julian_consistency(self):
        g = date(1990, 3, 10)
        h_date = HijriCalendar.gregorian_to_hijri(g.year, g.month, g.day)
        h_g = date(*HijriCalendar.hijri_to_gregorian(*h_date))
        assert h_g == g


# ==========================================
# ۶. تست‌های جامع مرزی و یکپارچگی (جدید)
# ==========================================

class TestHijriLeapDayConversions:
    """
    تست‌های مخصوص روز کبیسه در تقویم هجری (۳۰ ذی‌الحجه)
    در سال‌های کبیسه هجری، ماه دوازدهم ۳۰ روز دارد.
    """
    @pytest.mark.parametrize("h_year, is_leap", [
        (1441, True), (1442, False), (1443, False), (1444, True), (1445, False)
    ])
    def test_month_12_length(self, h_year, is_leap):
        if is_leap:
            # در سال کبیسه روز ۳۰ام باید معتبر باشد
            g_date = HijriCalendar.hijri_to_gregorian(h_year, 12, 30)
            assert HijriCalendar.gregorian_to_hijri(*g_date) == (h_year, 12, 30)
        else:
            # در سال غیر کبیسه روز ۳۰ام باید ValueError بدهد
            with pytest.raises(ValueError):
                HijriCalendar.hijri_to_gregorian(h_year, 12, 30)
            
            # اما روز ۲۹ام باید معتبر باشد
            g_date = HijriCalendar.hijri_to_gregorian(h_year, 12, 29)
            assert HijriCalendar.gregorian_to_hijri(*g_date) == (h_year, 12, 29)


class TestHijriRoundTripIntegrity:
    """
    تست یکپارچگی تبدیل در یک بازه طولانی (۱۰ سال میلادی)
    برای اطمینان از اینکه هیچ روزی در تبدیل گم نمی‌شود یا تکرار نمی‌شود.
    """
    def test_10_years_continuous_roundtrip(self):
        current = date(2015, 1, 1)
        end = date(2024, 12, 31)
        
        consecutive_days = 0
        last_hijri = None
        
        while current <= end:
            h_date = HijriCalendar.gregorian_to_hijri(current.year, current.month, current.day)
            
            # تست رفت و برگشت باید دقیقاً مطابق اصل باشد
            back_g = HijriCalendar.hijri_to_gregorian(*h_date)
            assert back_g == (current.year, current.month, current.day), f"Failed at {current}"
            
            # تاریخ‌های هجری باید دقیقاً متوالی باشند (بدون پرش یا هم‌پوشانی)
            if last_hijri:
                prev_g = date(*HijriCalendar.hijri_to_gregorian(*last_hijri))
                curr_g = date(*back_g)
                assert (curr_g - prev_g).days == 1, f"Gap or overlap at {current}"
                
            last_hijri = h_date
            consecutive_days += 1
            current += timedelta(days=1)
            
        # سال‌های ۲۰۱۶، ۲۰۲۰ و ۲۰۲۴ کبیسه میلادی هستند.
        # مجموع روزها: 3653 روز
        assert consecutive_days == 3653


class TestHijriBoundaries:
    """تست مرزهای ماه و سال در تقویم هجری"""
    
    @pytest.mark.parametrize("month", range(1, 12))
    def test_month_transitions(self, month):
        """تست گذر از آخرین روز یک ماه به اولین روز ماه بعد"""
        year = 1442 # یک سال غیر کبیسه برای ثبات طول ماه‌های زوج و فرد
        is_odd = (month % 2 != 0)
        max_days = 30 if is_odd else 29
        
        last_day_g = date(*HijriCalendar.hijri_to_gregorian(year, month, max_days))
        next_month = (month % 12) + 1
        next_year = year if month < 12 else year + 1
        first_day_next_g = date(*HijriCalendar.hijri_to_gregorian(next_year, next_month, 1))
        
        assert (first_day_next_g - last_day_g).days == 1

    def test_year_transition_non_leap(self):
        """گذار از سال غیر کبیسه به سال بعد"""
        last_day_g = date(*HijriCalendar.hijri_to_gregorian(1442, 12, 29))
        first_day_next_g = date(*HijriCalendar.hijri_to_gregorian(1443, 1, 1))
        assert (first_day_next_g - last_day_g).days == 1

    def test_year_transition_leap(self):
        """گذار از سال کبیسه به سال بعد"""
        last_day_g = date(*HijriCalendar.hijri_to_gregorian(1441, 12, 30))
        first_day_next_g = date(*HijriCalendar.hijri_to_gregorian(1442, 1, 1))
        assert (first_day_next_g - last_day_g).days == 1