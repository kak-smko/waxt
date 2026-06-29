from datetime import datetime, time, timedelta
from typing import Optional, Tuple

import pytz

from waxt.calendar_converters import HijriCalendar, JalaliCalendar


class Date:
    CALENDAR_JALALI = "jalali"
    CALENDAR_HIJRI = "hijri"
    CALENDAR_GREGORIAN = "gregorian"

    def __init__(self, timezone: str, calendar: str):
        self.timezone = timezone
        self.calendar = calendar
        self._validate_calendar()

    def _validate_calendar(self):
        valid_calendars = [
            self.CALENDAR_JALALI,
            self.CALENDAR_HIJRI,
            self.CALENDAR_GREGORIAN,
        ]
        if self.calendar not in valid_calendars:
            raise ValueError(
                f"Invalid calendar type: {self.calendar}. "
                f"Must be one of: {', '.join(valid_calendars)}"
            )

    def _get_timezone(self) -> pytz.timezone:
        try:
            return pytz.timezone(self.timezone)
        except Exception:
            return pytz.UTC

    def now_utc(self) -> datetime:
        return datetime.now(pytz.UTC)

    def now(self) -> datetime:
        return datetime.now(self._get_timezone())

    def to_company_timezone(self, utc_dt: datetime) -> datetime:
        if utc_dt is None:
            return None

        if utc_dt.tzinfo is None:
            utc_dt = pytz.UTC.localize(utc_dt)

        return utc_dt.astimezone(self._get_timezone())

    def to_utc(self, company_dt: datetime) -> datetime:
        if company_dt is None:
            return None

        if company_dt.tzinfo is None:
            company_dt = self._get_timezone().localize(company_dt)

        return company_dt.astimezone(pytz.UTC)

    def get_date_components(self, dt: datetime) -> Tuple[int, int, int]:
        if dt is None:
            return None

        if dt.tzinfo is None:
            dt = self._get_timezone().localize(dt)
        else:
            dt = dt.astimezone(self._get_timezone())

        if self.calendar == self.CALENDAR_JALALI:
            return JalaliCalendar.gregorian_to_jalali(dt.year, dt.month, dt.day)

        elif self.calendar == self.CALENDAR_HIJRI:
            return HijriCalendar.gregorian_to_hijri(dt.year, dt.month, dt.day)

        else:
            return (dt.year, dt.month, dt.day)

    def format_date(
        self, dt: datetime, format_str: Optional[str] = None, include_time: bool = False
    ) -> str:
        if dt is None:
            return ""

        if dt.tzinfo is None:
            dt = self._get_timezone().localize(dt)
        else:
            dt = dt.astimezone(self._get_timezone())

        year, month, day = self.get_date_components(dt)

        if format_str:
            result = format_str
            result = result.replace("%Y", f"{year:04d}")
            result = result.replace("%m", f"{month:02d}")
            result = result.replace("%d", f"{day:02d}")
            result = result.replace("%H", f"{dt.hour:02d}")
            result = result.replace("%M", f"{dt.minute:02d}")
            result = result.replace("%S", f"{dt.second:02d}")
            return result

        date_str = f"{year:04d}/{month:02d}/{day:02d}"

        if include_time:
            time_str = f"{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"
            return f"{date_str} {time_str}"

        return date_str

    def parse_date(
        self,
        date_str: str,
        format_str: Optional[str] = None,
        time_component: Optional[time] = None,
    ) -> datetime:
        if not date_str:
            return None

        if time_component is None:
            time_component = time(0, 0, 0)

        parts = date_str.replace("-", "/").split()
        date_part = parts[0]
        time_part = parts[1] if len(parts) > 1 else None

        date_components = date_part.split("/")
        if len(date_components) != 3:
            raise ValueError(f"Invalid date format: {date_str}")

        year = int(date_components[0])
        month = int(date_components[1])
        day = int(date_components[2])

        if self.calendar == self.CALENDAR_JALALI:
            g_year, g_month, g_day = JalaliCalendar.jalali_to_gregorian(
                year, month, day
            )
        elif self.calendar == self.CALENDAR_HIJRI:
            g_year, g_month, g_day = HijriCalendar.hijri_to_gregorian(year, month, day)
        else:
            g_year, g_month, g_day = year, month, day

        if time_part:
            time_components = time_part.split(":")
            hour = int(time_components[0]) if len(time_components) > 0 else 0
            minute = int(time_components[1]) if len(time_components) > 1 else 0
            second = int(time_components[2]) if len(time_components) > 2 else 0
            time_component = time(hour, minute, second)

        return datetime(
            g_year,
            g_month,
            g_day,
            time_component.hour,
            time_component.minute,
            time_component.second,
        )

    def get_month_name(self, month: int, locale: str = "fa") -> str:
        if self.calendar == self.CALENDAR_JALALI:
            jalali_months_fa = [
                "فروردین",
                "اردیبهشت",
                "خرداد",
                "تیر",
                "مرداد",
                "شهریور",
                "مهر",
                "آبان",
                "آذر",
                "دی",
                "بهمن",
                "اسفند",
            ]
            jalali_months_en = [
                "Farvardin",
                "Ordibehesht",
                "Khordad",
                "Tir",
                "Mordad",
                "Shahrivar",
                "Mehr",
                "Aban",
                "Azar",
                "Dey",
                "Bahman",
                "Esfand",
            ]
            months = jalali_months_fa if locale == "fa" else jalali_months_en
            return months[month - 1] if 1 <= month <= 12 else ""

        elif self.calendar == self.CALENDAR_HIJRI:
            hijri_months_ar = [
                "محرم",
                "صفر",
                "ربیع الاول",
                "ربیع الثانی",
                "جمادی الاول",
                "جمادی الثانی",
                "رجب",
                "شعبان",
                "رمضان",
                "شوال",
                "ذی القعده",
                "ذی الحجه",
            ]
            hijri_months_en = [
                "Muharram",
                "Safar",
                "Rabi' al-awwal",
                "Rabi' al-thani",
                "Jumada al-awwal",
                "Jumada al-thani",
                "Rajab",
                "Sha'ban",
                "Ramadan",
                "Shawwal",
                "Dhu al-Qi'dah",
                "Dhu al-Hijjah",
            ]
            months = hijri_months_ar if locale in ["fa", "ar"] else hijri_months_en
            return months[month - 1] if 1 <= month <= 12 else ""

        else:
            gregorian_months_fa = [
                "ژانویه",
                "فوریه",
                "مارس",
                "آوریل",
                "مه",
                "ژوئن",
                "جولای",
                "اوت",
                "سپتامبر",
                "اکتبر",
                "نوامبر",
                "دسامبر",
            ]
            gregorian_months_en = [
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ]
            months = gregorian_months_fa if locale == "fa" else gregorian_months_en
            return months[month - 1] if 1 <= month <= 12 else ""

    def add_days(self, dt: datetime, days: int) -> datetime:
        if dt is None:
            return None
        return dt + timedelta(days=days)

    def add_months(self, dt: datetime, months: int) -> datetime:
        if dt is None:
            return None

        year, month, day = self.get_date_components(dt)

        total_months = year * 12 + month - 1 + months
        new_year = total_months // 12
        new_month = (total_months % 12) + 1

        if self.calendar == self.CALENDAR_JALALI:
            if new_month <= 6:
                max_day = 31
            elif new_month <= 11:
                max_day = 30
            else:
                max_day = 30 if JalaliCalendar.is_leap(new_year) else 29
            new_day = min(day, max_day)

            g_year, g_month, g_day = JalaliCalendar.jalali_to_gregorian(
                new_year, new_month, new_day
            )

        elif self.calendar == self.CALENDAR_HIJRI:
            if new_month % 2 == 1:
                max_day = 30
            elif new_month == 12 and HijriCalendar.is_leap(new_year):
                max_day = 30
            else:
                max_day = 29
            new_day = min(day, max_day)

            g_year, g_month, g_day = HijriCalendar.hijri_to_gregorian(
                new_year, new_month, new_day
            )

        else:
            new_day = day
            while True:
                try:
                    greg_dt = datetime(
                        new_year, new_month, new_day, dt.hour, dt.minute, dt.second
                    )
                    break
                except ValueError:
                    new_day -= 1
            g_year, g_month, g_day = new_year, new_month, new_day

        greg_dt = datetime(g_year, g_month, g_day, dt.hour, dt.minute, dt.second)

        if dt.tzinfo:
            greg_dt = (
                dt.tzinfo.localize(greg_dt)
                if hasattr(dt.tzinfo, "localize")
                else greg_dt.replace(tzinfo=dt.tzinfo)
            )

        return greg_dt

    def get_year_month(self, dt: datetime) -> Tuple[int, int]:
        year, month, _ = self.get_date_components(dt)
        return (year, month)

    def start_of_day(self, dt: datetime) -> datetime:
        if dt is None:
            return None
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)

    def end_of_day(self, dt: datetime) -> datetime:
        if dt is None:
            return None
        return dt.replace(hour=23, minute=59, second=59, microsecond=999999)


def create_date_service_for_company(company) -> Date:
    timezone = getattr(company, "timezone", "UTC")
    calendar = getattr(company, "calendar", "gregorian")
    return Date(timezone=timezone, calendar=calendar)
