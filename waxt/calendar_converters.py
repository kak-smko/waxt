import math
from typing import Tuple


class JalaliCalendar:
    BREAKS = [
        -61,
        9,
        38,
        199,
        426,
        686,
        756,
        818,
        1111,
        1181,
        1210,
        1635,
        2060,
        2097,
        2192,
        2262,
        2324,
        2394,
        2456,
        3178,
    ]

    @staticmethod
    def is_leap(j_year: int) -> bool:
        cycle_start = 1391
        position = ((j_year - cycle_start) % 33) + 1
        leap_positions = [1, 5, 9, 13, 17, 21, 25, 29]
        return position in leap_positions

    @staticmethod
    def jalali_to_gregorian(
        j_year: int, j_month: int, j_day: int
    ) -> Tuple[int, int, int]:
        if not (1 <= j_month <= 12):
            raise ValueError(f"Invalid Jalali month: {j_month}. Must be 1-12.")

        if j_month <= 6:
            max_days = 31
        elif j_month <= 11:
            max_days = 30
        else:
            max_days = 30 if JalaliCalendar.is_leap(j_year) else 29

        if not (1 <= j_day <= max_days):
            raise ValueError(
                f"Invalid Jalali day: {j_day} for month {j_month}. "
                f"Max days: {max_days}."
            )

        gy = j_year + 621

        breaks = JalaliCalendar.BREAKS
        leap = -14
        jp = breaks[0]

        jump = 0
        for i in range(1, len(breaks)):
            jm = breaks[i]
            jump = jm - jp
            if j_year < jm:
                break
            leap = leap + (jump // 33) * 8 + ((jump % 33) // 4)
            jp = jm

        n = j_year - jp

        if jump - n < 6:
            n = n - jump + ((jump + 4) // 33) * 33

        leap = leap + ((n + 1) // 33) * 8 + (((n % 33) + 3) // 4)

        if (jump % 33) == 4 and (jump - n) == 4:
            leap += 1

        gy_offset = gy

        if j_month <= 6:
            j_day_of_year = (j_month - 1) * 31 + j_day
        else:
            j_day_of_year = 6 * 31 + (j_month - 7) * 30 + j_day

        g_day_of_year = j_day_of_year + 79

        if ((gy_offset % 4 == 0) and (gy_offset % 100 != 0)) or (gy_offset % 400 == 0):
            is_gregorian_leap = True
        else:
            is_gregorian_leap = False

        if g_day_of_year > (366 if is_gregorian_leap else 365):
            g_day_of_year -= 366 if is_gregorian_leap else 365
            gy_offset += 1
            is_gregorian_leap = ((gy_offset % 4 == 0) and (gy_offset % 100 != 0)) or (
                gy_offset % 400 == 0
            )

        month_days = [
            31,
            29 if is_gregorian_leap else 28,
            31,
            30,
            31,
            30,
            31,
            31,
            30,
            31,
            30,
            31,
        ]
        g_month = 1
        for days in month_days:
            if g_day_of_year <= days:
                g_day = g_day_of_year
                break
            g_day_of_year -= days
            g_month += 1

        return (gy_offset, g_month, int(g_day))

    @staticmethod
    def gregorian_to_jalali(
        g_year: int, g_month: int, g_day: int
    ) -> Tuple[int, int, int]:
        month_days = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        if ((g_year % 4 == 0) and (g_year % 100 != 0)) or (g_year % 400 == 0):
            month_days[2] = 29

        g_day_of_year = sum(month_days[:g_month]) + g_day

        march_day = 80
        if ((g_year % 4 == 0) and (g_year % 100 != 0)) or (g_year % 400 == 0):
            march_day = 80

        if g_day_of_year >= march_day:
            j_day_of_year = g_day_of_year - march_day + 1
            j_year = g_year - 621
        else:
            prev_year = g_year - 1
            if ((prev_year % 4 == 0) and (prev_year % 100 != 0)) or (
                prev_year % 400 == 0
            ):
                days_in_prev_year = 366
            else:
                days_in_prev_year = 365

            j_day_of_year = days_in_prev_year - march_day + g_day_of_year + 1
            j_year = g_year - 622

        if JalaliCalendar.is_leap(j_year):
            j_year_length = 366
        else:
            j_year_length = 365

        if j_day_of_year > j_year_length:
            j_day_of_year -= j_year_length
            j_year += 1

        if j_day_of_year <= 186:
            j_month = math.ceil(j_day_of_year / 31)
            j_day = j_day_of_year - (j_month - 1) * 31
        else:
            remaining = j_day_of_year - 186
            j_month = 6 + math.ceil(remaining / 30)
            j_day = remaining - (j_month - 7) * 30

        return (int(j_year), int(j_month), int(j_day))


class HijriCalendar:
    EPOCH_GREGORIAN_YEAR = 622
    EPOCH_GREGORIAN_MONTH = 7
    EPOCH_GREGORIAN_DAY = 19

    @staticmethod
    def is_leap(h_year: int) -> bool:
        return (11 * h_year + 25) % 30 < 11

    @staticmethod
    def hijri_to_gregorian(
        h_year: int, h_month: int, h_day: int
    ) -> Tuple[int, int, int]:
        if not (1 <= h_month <= 12):
            raise ValueError(f"Invalid Hijri month: {h_month}. Must be 1-12.")

        if h_month % 2 == 1:
            max_days = 30
        elif h_month == 12 and HijriCalendar.is_leap(h_year):
            max_days = 30
        else:
            max_days = 29

        if not (1 <= h_day <= max_days):
            raise ValueError(
                f"Invalid Hijri day: {h_day} for month {h_month} year {h_year}. "
                f"Max days: {max_days}."
            )

        total_days = h_day

        for m in range(1, h_month):
            if m % 2 == 1:
                total_days += 30
            else:
                total_days += 29

        total_days += (h_year - 1) * 354
        total_days += (11 * (h_year - 1) + 25) // 30

        from datetime import date, timedelta

        epoch = date(
            HijriCalendar.EPOCH_GREGORIAN_YEAR,
            HijriCalendar.EPOCH_GREGORIAN_MONTH,
            HijriCalendar.EPOCH_GREGORIAN_DAY,
        )

        result_date = epoch + timedelta(days=total_days - 1)

        return (result_date.year, result_date.month, result_date.day)

    @staticmethod
    def gregorian_to_hijri(
        g_year: int, g_month: int, g_day: int
    ) -> Tuple[int, int, int]:
        from datetime import date

        epoch = date(
            HijriCalendar.EPOCH_GREGORIAN_YEAR,
            HijriCalendar.EPOCH_GREGORIAN_MONTH,
            HijriCalendar.EPOCH_GREGORIAN_DAY,
        )

        target = date(g_year, g_month, g_day)
        days_from_epoch = (target - epoch).days + 1

        if days_from_epoch < 1:
            return (1, 1, 1)

        h_year = int(days_from_epoch / 354.36667) + 1

        while True:
            year_start = (h_year - 1) * 354 + (11 * (h_year - 1) + 25) // 30
            year_end = h_year * 354 + (11 * h_year + 25) // 30

            if year_start < days_from_epoch <= year_end:
                break
            elif days_from_epoch > year_end:
                h_year += 1
            else:
                h_year -= 1

        day_of_year = days_from_epoch - year_start

        h_month = 1
        for m in range(1, 13):
            if m % 2 == 1:
                month_days = 30
            elif m == 12 and HijriCalendar.is_leap(h_year):
                month_days = 30
            else:
                month_days = 29

            if day_of_year <= month_days:
                h_day = day_of_year
                break
            day_of_year -= month_days
            h_month += 1

        return (int(h_year), int(h_month), int(h_day))
