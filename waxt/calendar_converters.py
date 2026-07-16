from typing import Tuple


class JalaliCalendar:
    # Break points of the 33-year leap cycle approximation.
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
    def _div(a: int, b: int) -> int:
        q = a // b
        if (a % b != 0) and ((a < 0) != (b < 0)):
            q += 1
        return q

    @staticmethod
    def _mod(a: int, b: int) -> int:
        return a - JalaliCalendar._div(a, b) * b

    @staticmethod
    def _jal_cal(j_year: int) -> Tuple[int, int, int]:
        if j_year < JalaliCalendar.BREAKS[0] or j_year >= JalaliCalendar.BREAKS[-1]:
            raise ValueError(
                f"Jalali year {j_year} is outside the supported range "
                f"({JalaliCalendar.BREAKS[0]}..{JalaliCalendar.BREAKS[-1] - 1})."
            )
        breaks = JalaliCalendar.BREAKS
        bl = len(breaks)
        gy = j_year + 621
        leap_j = -14
        jp = breaks[0]

        jump = 0
        i = 1
        while i < bl:
            jm = breaks[i]
            jump = jm - jp
            if j_year < jm:
                break
            leap_j = (
                leap_j
                + JalaliCalendar._div(jump, 33) * 8
                + JalaliCalendar._div(JalaliCalendar._mod(jump, 33), 4)
            )
            jp = jm
            i += 1

        n = j_year - jp

        leap_j = (
            leap_j
            + JalaliCalendar._div(n, 33) * 8
            + JalaliCalendar._div(JalaliCalendar._mod(n, 33) + 3, 4)
        )
        if JalaliCalendar._mod(jump, 33) == 4 and jump - n == 4:
            leap_j += 1

        leap_g = (
            JalaliCalendar._div(gy, 4)
            - JalaliCalendar._div((JalaliCalendar._div(gy, 100) + 1) * 3, 4)
            - 150
        )
        march = 20 + leap_j - leap_g

        if jump - n < 6:
            n = n - jump + JalaliCalendar._div(jump + 4, 33) * 33
        leap = JalaliCalendar._mod(JalaliCalendar._mod(n + 1, 33) - 1, 4)
        if leap == -1:
            leap = 4

        return (leap, gy, march)

    @staticmethod
    def _g2d(gy: int, gm: int, gd: int) -> int:
        d = (
            JalaliCalendar._div(
                (gy + JalaliCalendar._div(gm - 8, 6) + 100100) * 1461, 4
            )
            + JalaliCalendar._div(153 * JalaliCalendar._mod(gm + 9, 12) + 2, 5)
            + gd
            - 34840408
        )
        d = (
            d
            - JalaliCalendar._div(
                JalaliCalendar._div(gy + 100100 + JalaliCalendar._div(gm - 8, 6), 100)
                * 3,
                4,
            )
            + 752
        )
        return d

    @staticmethod
    def _d2g(jdn: int) -> Tuple[int, int, int]:
        j = 4 * jdn + 139361631
        j = (
            j
            + JalaliCalendar._div(
                JalaliCalendar._div(4 * jdn + 183187720, 146097) * 3, 4
            )
            * 4
            - 3908
        )
        i = JalaliCalendar._div(JalaliCalendar._mod(j, 1461), 4) * 5 + 308
        gd = JalaliCalendar._div(JalaliCalendar._mod(i, 153), 5) + 1
        gm = JalaliCalendar._mod(JalaliCalendar._div(i, 153), 12) + 1
        gy = JalaliCalendar._div(j, 1461) - 100100 + JalaliCalendar._div(8 - gm, 6)
        return (gy, gm, gd)

    @staticmethod
    def is_leap(j_year: int) -> bool:
        leap, _, _ = JalaliCalendar._jal_cal(j_year)
        return leap == 0

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

        _, gy, march = JalaliCalendar._jal_cal(j_year)

        jdn = (
            JalaliCalendar._g2d(gy, 3, march)
            + (j_month - 1) * 31
            - JalaliCalendar._div(j_month, 7) * (j_month - 7)
            + j_day
            - 1
        )

        g_year, g_month, g_day = JalaliCalendar._d2g(jdn)

        return (g_year, g_month, g_day)

    @staticmethod
    def gregorian_to_jalali(
        g_year: int, g_month: int, g_day: int
    ) -> Tuple[int, int, int]:
        jdn = JalaliCalendar._g2d(g_year, g_month, g_day)

        j_year = g_year - 621
        leap, jgy, march = JalaliCalendar._jal_cal(j_year)
        jdn1f = JalaliCalendar._g2d(jgy, 3, march)

        k = jdn - jdn1f
        if k >= 0:
            if k <= 185:
                j_month = 1 + JalaliCalendar._div(k, 31)
                j_day = JalaliCalendar._mod(k, 31) + 1
                return (j_year, j_month, j_day)
            k -= 186
        else:
            j_year -= 1
            k += 179
            if leap == 1:
                k += 1

        j_month = 7 + JalaliCalendar._div(k, 30)
        j_day = JalaliCalendar._mod(k, 30) + 1

        return (j_year, j_month, j_day)


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
            raise ValueError("Date is before Hijri epoch.")

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
