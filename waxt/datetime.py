"""Calendar-aware datetime value type.

``DateTime`` mirrors Python's :class:`datetime.datetime` API while displaying
and accepting date fields in Gregorian, Jalali, or civil (tabular) Hijri.
Internally every value is stored as a standard Gregorian ``datetime`` so that
timezone handling, arithmetic, timestamps, and comparisons retain their normal
Python semantics.
"""

from __future__ import annotations

import re
import time as _time
from calendar import monthrange
from datetime import date as _date
from datetime import datetime as _datetime
from datetime import time as _datetime_time
from datetime import timedelta
from datetime import timezone as _timezone
from datetime import tzinfo as _tzinfo
from typing import Any, Optional, Tuple, Union

from waxt.calendar_converters import HijriCalendar, JalaliCalendar

_UNSET = object()


def _restore_datetime(value: _datetime, calendar: str) -> "DateTime":
    """Rebuild a DateTime during unpickling."""
    return DateTime.from_datetime(value, calendar=calendar)


class DateTime:
    """An immutable calendar-aware counterpart to ``datetime.datetime``.

    ``year``, ``month``, and ``day`` are interpreted using ``calendar``. All
    time fields and timezone behavior follow the standard library. Calendar
    conversion changes only the representation, never the represented wall
    time or instant.
    """

    CALENDAR_GREGORIAN = "gregorian"
    CALENDAR_JALALI = "jalali"
    CALENDAR_HIJRI = "hijri"
    CALENDARS = (CALENDAR_GREGORIAN, CALENDAR_JALALI, CALENDAR_HIJRI)

    __slots__ = ("_datetime", "_calendar", "_initialized")

    min: "DateTime"
    max: "DateTime"
    resolution = timedelta(microseconds=1)

    def __init__(
        self,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        microsecond: int = 0,
        tzinfo: Optional[_tzinfo] = None,
        *,
        fold: int = 0,
        calendar: str = CALENDAR_GREGORIAN,
    ) -> None:
        calendar = self._validate_calendar(calendar)
        g_year, g_month, g_day = self._to_gregorian(calendar, year, month, day)
        value = _datetime(
            g_year,
            g_month,
            g_day,
            hour,
            minute,
            second,
            microsecond,
            tzinfo,
            fold=fold,
        )
        object.__setattr__(self, "_datetime", value)
        object.__setattr__(self, "_calendar", calendar)
        object.__setattr__(self, "_initialized", True)

    def __setattr__(self, name: str, value: object) -> None:
        if getattr(self, "_initialized", False):
            raise AttributeError(f"{type(self).__name__!s} objects are immutable")
        object.__setattr__(self, name, value)

    @classmethod
    def _from_datetime(cls, value: _datetime, calendar: str) -> "DateTime":
        calendar = cls._validate_calendar(calendar)
        cls._from_gregorian(calendar, value.year, value.month, value.day)
        result = object.__new__(cls)
        object.__setattr__(result, "_datetime", value)
        object.__setattr__(result, "_calendar", calendar)
        object.__setattr__(result, "_initialized", True)
        return result

    @classmethod
    def from_datetime(
        cls, value: _datetime, *, calendar: str = CALENDAR_GREGORIAN
    ) -> "DateTime":
        """Create a value from a standard Gregorian ``datetime``."""
        if not isinstance(value, _datetime):
            raise TypeError("value must be a datetime.datetime instance")
        return cls._from_datetime(value, calendar)

    def to_datetime(self) -> _datetime:
        """Return the equivalent standard Gregorian ``datetime``."""
        return self._datetime

    def to_calendar(self, calendar: str) -> "DateTime":
        """Return the same datetime represented in another calendar."""
        return type(self)._from_datetime(self._datetime, calendar)

    @classmethod
    def _validate_calendar(cls, calendar: str) -> str:
        if not isinstance(calendar, str):
            raise TypeError("calendar must be a string")
        normalized = calendar.lower()
        if normalized not in cls.CALENDARS:
            raise ValueError(
                f"Invalid calendar: {calendar!r}. Must be one of: "
                f"{', '.join(cls.CALENDARS)}"
            )
        return normalized

    @staticmethod
    def _to_gregorian(
        calendar: str, year: int, month: int, day: int
    ) -> Tuple[int, int, int]:
        if calendar == DateTime.CALENDAR_JALALI:
            return JalaliCalendar.jalali_to_gregorian(year, month, day)
        if calendar == DateTime.CALENDAR_HIJRI:
            return HijriCalendar.hijri_to_gregorian(year, month, day)
        return (year, month, day)

    @staticmethod
    def _from_gregorian(
        calendar: str, year: int, month: int, day: int
    ) -> Tuple[int, int, int]:
        if calendar == DateTime.CALENDAR_JALALI:
            return JalaliCalendar.gregorian_to_jalali(year, month, day)
        if calendar == DateTime.CALENDAR_HIJRI:
            return HijriCalendar.gregorian_to_hijri(year, month, day)
        return (year, month, day)

    @property
    def calendar(self) -> str:
        return self._calendar

    @property
    def year(self) -> int:
        return self._date_fields[0]

    @property
    def month(self) -> int:
        return self._date_fields[1]

    @property
    def day(self) -> int:
        return self._date_fields[2]

    @property
    def _date_fields(self) -> Tuple[int, int, int]:
        value = self._datetime
        return self._from_gregorian(self.calendar, value.year, value.month, value.day)

    @property
    def hour(self) -> int:
        return self._datetime.hour

    @property
    def minute(self) -> int:
        return self._datetime.minute

    @property
    def second(self) -> int:
        return self._datetime.second

    @property
    def microsecond(self) -> int:
        return self._datetime.microsecond

    @property
    def tzinfo(self) -> Optional[_tzinfo]:
        return self._datetime.tzinfo

    @property
    def fold(self) -> int:
        return self._datetime.fold

    @classmethod
    def today(cls, *, calendar: str = CALENDAR_GREGORIAN) -> "DateTime":
        return cls._from_datetime(_datetime.today(), calendar)

    @classmethod
    def now(
        cls,
        tz: Optional[_tzinfo] = None,
        *,
        calendar: str = CALENDAR_GREGORIAN,
    ) -> "DateTime":
        return cls._from_datetime(_datetime.now(tz), calendar)

    @classmethod
    def utcnow(cls, *, calendar: str = CALENDAR_GREGORIAN) -> "DateTime":
        value = _datetime.now(_timezone.utc).replace(tzinfo=None)
        return cls._from_datetime(value, calendar)

    @classmethod
    def fromtimestamp(
        cls,
        timestamp: float,
        tz: Optional[_tzinfo] = None,
        *,
        calendar: str = CALENDAR_GREGORIAN,
    ) -> "DateTime":
        return cls._from_datetime(_datetime.fromtimestamp(timestamp, tz), calendar)

    @classmethod
    def utcfromtimestamp(
        cls, timestamp: float, *, calendar: str = CALENDAR_GREGORIAN
    ) -> "DateTime":
        value = _datetime.fromtimestamp(timestamp, _timezone.utc).replace(tzinfo=None)
        return cls._from_datetime(value, calendar)

    @classmethod
    def fromordinal(
        cls, ordinal: int, *, calendar: str = CALENDAR_GREGORIAN
    ) -> "DateTime":
        return cls._from_datetime(_datetime.fromordinal(ordinal), calendar)

    @classmethod
    def combine(
        cls,
        date: Union[_date, "DateTime"],
        time: _datetime_time,
        tzinfo: Any = _UNSET,
        *,
        calendar: Optional[str] = None,
    ) -> "DateTime":
        if not isinstance(time, _datetime_time):
            raise TypeError("time must be a datetime.time instance")
        if isinstance(date, DateTime):
            selected_calendar = calendar or date.calendar
            year, month, day = date.year, date.month, date.day
        elif isinstance(date, _date):
            selected_calendar = calendar or cls.CALENDAR_GREGORIAN
            year, month, day = date.year, date.month, date.day
        else:
            raise TypeError("date must be a datetime.date or DateTime instance")
        selected_tzinfo = time.tzinfo if tzinfo is _UNSET else tzinfo
        return cls(
            year,
            month,
            day,
            time.hour,
            time.minute,
            time.second,
            time.microsecond,
            selected_tzinfo,
            fold=time.fold,
            calendar=selected_calendar,
        )

    @classmethod
    def fromisoformat(
        cls, date_string: str, *, calendar: str = CALENDAR_GREGORIAN
    ) -> "DateTime":
        parsed = _datetime.fromisoformat(date_string)
        return cls(
            parsed.year,
            parsed.month,
            parsed.day,
            parsed.hour,
            parsed.minute,
            parsed.second,
            parsed.microsecond,
            parsed.tzinfo,
            fold=parsed.fold,
            calendar=calendar,
        )

    @classmethod
    def strptime(
        cls,
        date_string: str,
        format: str,
        *,
        calendar: str = CALENDAR_GREGORIAN,
    ) -> "DateTime":
        parsed = _datetime.strptime(date_string, format)
        return cls(
            parsed.year,
            parsed.month,
            parsed.day,
            parsed.hour,
            parsed.minute,
            parsed.second,
            parsed.microsecond,
            parsed.tzinfo,
            fold=parsed.fold,
            calendar=calendar,
        )

    def date(self) -> _date:
        """Return the underlying proleptic-Gregorian standard-library date."""
        return self._datetime.date()

    def time(self) -> _datetime_time:
        return self._datetime.time()

    def timetz(self) -> _datetime_time:
        return self._datetime.timetz()

    def replace(
        self,
        *,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
        hour: Optional[int] = None,
        minute: Optional[int] = None,
        second: Optional[int] = None,
        microsecond: Optional[int] = None,
        tzinfo: Any = _UNSET,
        fold: Optional[int] = None,
        calendar: Optional[str] = None,
    ) -> "DateTime":
        selected_calendar = self.calendar if calendar is None else calendar
        if selected_calendar != self.calendar and any(
            value is not None for value in (year, month, day)
        ):
            raise ValueError(
                "date fields and calendar cannot be changed in the same replace() call"
            )
        if selected_calendar != self.calendar:
            return self.to_calendar(selected_calendar).replace(
                hour=hour,
                minute=minute,
                second=second,
                microsecond=microsecond,
                tzinfo=tzinfo,
                fold=fold,
            )
        return type(self)(
            self.year if year is None else year,
            self.month if month is None else month,
            self.day if day is None else day,
            self.hour if hour is None else hour,
            self.minute if minute is None else minute,
            self.second if second is None else second,
            self.microsecond if microsecond is None else microsecond,
            self.tzinfo if tzinfo is _UNSET else tzinfo,
            fold=self.fold if fold is None else fold,
            calendar=self.calendar,
        )

    def astimezone(self, tz: Optional[_tzinfo] = None) -> "DateTime":
        return type(self)._from_datetime(self._datetime.astimezone(tz), self.calendar)

    def utcoffset(self) -> Optional[timedelta]:
        return self._datetime.utcoffset()

    def dst(self) -> Optional[timedelta]:
        return self._datetime.dst()

    def tzname(self) -> Optional[str]:
        return self._datetime.tzname()

    def timetuple(self) -> _time.struct_time:
        year, month, day = self._date_fields
        dst = self.dst()
        is_dst = -1 if dst is None else int(dst != timedelta(0))
        return _time.struct_time(
            (
                year,
                month,
                day,
                self.hour,
                self.minute,
                self.second,
                self.weekday(),
                self._day_of_year(),
                is_dst,
            )
        )

    def utctimetuple(self) -> _time.struct_time:
        value = self._datetime
        if value.tzinfo is not None:
            offset = value.utcoffset()
            if offset is not None:
                value = (value - offset).replace(tzinfo=None)
        converted = type(self)._from_datetime(value, self.calendar)
        fields = converted.timetuple()
        return _time.struct_time(tuple(fields[:8]) + (0,))

    def _day_of_year(self) -> int:
        first = type(self)(self.year, 1, 1, calendar=self.calendar)
        return (self._datetime.date() - first._datetime.date()).days + 1

    def toordinal(self) -> int:
        return self._datetime.toordinal()

    def timestamp(self) -> float:
        return self._datetime.timestamp()

    def weekday(self) -> int:
        return self._datetime.weekday()

    def isoweekday(self) -> int:
        return self._datetime.isoweekday()

    def isocalendar(self) -> tuple:
        """Return the Gregorian ISO year, week, and weekday tuple."""
        result = self._datetime.isocalendar()
        return tuple(result)

    def isoformat(self, sep: str = "T", timespec: str = "auto") -> str:
        if not isinstance(sep, str) or len(sep) != 1:
            raise TypeError("isoformat() argument 1 must be a unicode character")
        date_part = f"{self.year:04d}-{self.month:02d}-{self.day:02d}"
        return date_part + sep + self.timetz().isoformat(timespec=timespec)

    def ctime(self) -> str:
        weekday = self._weekday_names()[0][self.weekday()]
        month = self._month_names()[0][self.month - 1]
        return (
            f"{weekday} {month} {self.day:2d} "
            f"{self.hour:02d}:{self.minute:02d}:{self.second:02d} {self.year:04d}"
        )

    def _weekday_names(self) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
        if self.calendar == self.CALENDAR_JALALI:
            abbreviated = ("Dos", "Ses", "Cha", "Pan", "Jom", "Sha", "Yek")
            full = (
                "Doshanbeh",
                "Seshanbeh",
                "Chaharshanbeh",
                "Panjshanbeh",
                "Jomeh",
                "Shanbeh",
                "Yekshanbeh",
            )
        elif self.calendar == self.CALENDAR_HIJRI:
            abbreviated = ("Ith", "Thu", "Arb", "Kha", "Jum", "Sab", "Aha")
            full = (
                "al-Ithnayn",
                "ath-Thulatha",
                "al-Arbia",
                "al-Khamis",
                "al-Jumah",
                "as-Sabt",
                "al-Ahad",
            )
        else:
            abbreviated = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
            full = (
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            )
        return abbreviated, full

    def _month_names(self) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
        if self.calendar == self.CALENDAR_JALALI:
            full = (
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
            )
        elif self.calendar == self.CALENDAR_HIJRI:
            full = (
                "Muharram",
                "Safar",
                "Rabi al-awwal",
                "Rabi al-thani",
                "Jumada al-awwal",
                "Jumada al-thani",
                "Rajab",
                "Shaban",
                "Ramadan",
                "Shawwal",
                "Dhu al-Qidah",
                "Dhu al-Hijjah",
            )
        else:
            full = (
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
            )
        abbreviated = tuple(name[:3] for name in full)
        return abbreviated, full

    def strftime(self, format: str) -> str:
        if self.calendar == self.CALENDAR_GREGORIAN:
            return self._datetime.strftime(format)

        abbreviated, full = self._month_names()
        replacements = {
            "Y": f"{self.year:04d}",
            "y": f"{self.year % 100:02d}",
            "m": f"{self.month:02d}",
            "d": f"{self.day:02d}",
            "j": f"{self._day_of_year():03d}",
            "b": abbreviated[self.month - 1],
            "B": full[self.month - 1],
        }
        tokens = {}

        def substitute(match: re.Match[str]) -> str:
            directive = match.group(1)
            if directive == "%":
                return "%%"
            token = f"__WAXT_{len(tokens)}__"
            tokens[token] = replacements[directive]
            return token

        delegated_format = re.sub(r"%([YymdjbB%])", substitute, format)
        result = self._datetime.strftime(delegated_format)
        for token, replacement in tokens.items():
            result = result.replace(token, replacement)
        return result

    def __format__(self, format_spec: str) -> str:
        return self.strftime(format_spec) if format_spec else str(self)

    def __str__(self) -> str:
        return self.isoformat(" ")

    def __repr__(self) -> str:
        arguments = (
            f"{self.year}, {self.month}, {self.day}, {self.hour}, {self.minute}, "
            f"{self.second}, {self.microsecond}"
        )
        extras = []
        if self.tzinfo is not None:
            extras.append(f"tzinfo={self.tzinfo!r}")
        if self.fold:
            extras.append(f"fold={self.fold}")
        if self.calendar != self.CALENDAR_GREGORIAN:
            extras.append(f"calendar={self.calendar!r}")
        suffix = f", {', '.join(extras)}" if extras else ""
        return f"DateTime({arguments}{suffix})"

    @staticmethod
    def _coerce_other(other: object) -> Any:
        if isinstance(other, DateTime):
            return other._datetime
        if isinstance(other, _datetime):
            return other
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        coerced = self._coerce_other(other)
        if coerced is NotImplemented:
            return False
        return self._datetime == coerced

    def __lt__(self, other: object) -> bool:
        coerced = self._coerce_other(other)
        if coerced is NotImplemented:
            return NotImplemented
        return self._datetime < coerced

    def __le__(self, other: object) -> bool:
        coerced = self._coerce_other(other)
        if coerced is NotImplemented:
            return NotImplemented
        return self._datetime <= coerced

    def __gt__(self, other: object) -> bool:
        coerced = self._coerce_other(other)
        if coerced is NotImplemented:
            return NotImplemented
        return self._datetime > coerced

    def __ge__(self, other: object) -> bool:
        coerced = self._coerce_other(other)
        if coerced is NotImplemented:
            return NotImplemented
        return self._datetime >= coerced

    def __hash__(self) -> int:
        return hash(self._datetime)

    def add_days(self, days: int) -> "DateTime":
        return self + timedelta(days=days)

    def add_months(self, months: int) -> "DateTime":
        total_months = self.year * 12 + self.month - 1 + months
        new_year, month_index = divmod(total_months, 12)
        new_month = month_index + 1

        if self.calendar == self.CALENDAR_JALALI:
            if new_month <= 6:
                max_day = 31
            elif new_month <= 11:
                max_day = 30
            else:
                max_day = 30 if JalaliCalendar.is_leap(new_year) else 29
        elif self.calendar == self.CALENDAR_HIJRI:
            if new_month % 2 == 1:
                max_day = 30
            elif new_month == 12 and HijriCalendar.is_leap(new_year):
                max_day = 30
            else:
                max_day = 29
        else:
            max_day = monthrange(new_year, new_month)[1]

        return type(self)(
            new_year,
            new_month,
            min(self.day, max_day),
            self.hour,
            self.minute,
            self.second,
            self.microsecond,
            self.tzinfo,
            fold=self.fold,
            calendar=self.calendar,
        )

    def __add__(self, other: object) -> "DateTime":
        if not isinstance(other, timedelta):
            return NotImplemented
        return type(self)._from_datetime(self._datetime + other, self.calendar)

    def __radd__(self, other: object) -> "DateTime":
        return self.__add__(other)

    def __sub__(self, other: object) -> Union["DateTime", timedelta]:
        if isinstance(other, timedelta):
            return type(self)._from_datetime(self._datetime - other, self.calendar)
        coerced = self._coerce_other(other)
        if coerced is NotImplemented:
            return NotImplemented
        return self._datetime - coerced

    def __rsub__(self, other: object) -> timedelta:
        if isinstance(other, _datetime):
            return other - self._datetime
        return NotImplemented

    def __reduce__(self) -> tuple:
        return (_restore_datetime, (self._datetime, self.calendar))


DateTime.min = DateTime.from_datetime(_datetime.min)
DateTime.max = DateTime.from_datetime(_datetime.max)

# A lowercase alias is provided for users who prefer the standard module's
# class naming convention: ``from waxt.datetime import datetime``.
datetime = DateTime

__all__ = ["DateTime", "datetime"]
