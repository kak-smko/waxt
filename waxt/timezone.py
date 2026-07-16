"""Country-based timezone lookup.

Country metadata is bundled directly in this module so lookups work without
external data files.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from datetime import tzinfo as _tzinfo
from functools import lru_cache
from types import MappingProxyType
from typing import Mapping, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

__all__ = ["Timezone", "CountryTimezone", "COUNTRIES", "country", "tzinfo"]


class Timezone(_tzinfo):
    """An IANA timezone selected from the bundled country data.

    Date-aware operations use :class:`zoneinfo.ZoneInfo`, including daylight-
    saving transitions and historical offset changes. The bundled offset is
    retained for calls without a datetime and as a fallback when the IANA zone
    is unavailable.
    """

    __slots__ = ("name", "offset_minutes", "_offset", "_zone")

    def __init__(self, name: str, offset_minutes: int) -> None:
        if not isinstance(name, str):
            raise TypeError("timezone name must be a string")
        if not isinstance(offset_minutes, int):
            raise TypeError("timezone offset must be an integer number of minutes")
        if not -1439 <= offset_minutes <= 1439:
            raise ValueError("timezone offset must be strictly between -24h and +24h")

        self.name = name
        self.offset_minutes = offset_minutes
        self._offset = timedelta(minutes=offset_minutes)
        try:
            self._zone: Optional[ZoneInfo] = ZoneInfo(name)
        except ZoneInfoNotFoundError:
            self._zone = None

    @property
    def zone(self) -> str:
        """Return the descriptive IANA name from the country data."""
        return self.name

    def utcoffset(self, dt: Optional[datetime]) -> timedelta:
        if dt is None or self._zone is None:
            return self._offset
        offset = self._zone.utcoffset(dt.replace(tzinfo=self._zone))
        return self._offset if offset is None else offset

    def dst(self, dt: Optional[datetime]) -> timedelta:
        if dt is None or self._zone is None:
            return timedelta(0)
        offset = self._zone.dst(dt.replace(tzinfo=self._zone))
        return timedelta(0) if offset is None else offset

    def tzname(self, dt: Optional[datetime]) -> str:
        return self.name

    def fromutc(self, dt: datetime) -> datetime:
        if dt.tzinfo is not self:
            raise ValueError("fromutc: dt.tzinfo is not self")
        if self._zone is None:
            return super().fromutc(dt)

        zoned = self._zone.fromutc(dt.replace(tzinfo=self._zone))
        return zoned.replace(tzinfo=self)

    def __repr__(self) -> str:
        return f"Timezone(name={self.name!r}, offset_minutes={self.offset_minutes!r})"


@dataclass(frozen=True, slots=True)
class CountryTimezone:
    """Timezone and locale defaults for an ISO 3166-1 alpha-2 country code."""

    code: str
    name: str
    timezone: str
    offset: int
    week: int
    calendar: str = "gregorian"
    rtl: bool = False

    @property
    def tzinfo(self) -> Timezone:
        """Return the IANA timezone for this country."""
        return Timezone(self.timezone, self.offset)


# Calendar identifiers follow Unicode CLDR calendarPreferenceData. ``rtl``
# reflects the direction of the territory's dominant written locale, rather
# than whether any minority or additional official language is RTL.
_COUNTRY_DATA = (
    ("AF", "Afghanistan", "Asia/Kabul", 270, 6, "persian", True),
    ("AL", "Albania", "Europe/Tirane", 60, 1, "gregorian", False),
    ("DZ", "Algeria", "Africa/Algiers", 60, 6, "gregorian", True),
    ("AS", "American Samoa", "Pacific/Pago_Pago", -660, 0, "gregorian", False),
    ("AD", "Andorra", "Europe/Andorra", 60, 1, "gregorian", False),
    ("AO", "Angola", "Africa/Luanda", 60, 1, "gregorian", False),
    ("AI", "Anguilla", "America/Anguilla", -240, 1, "gregorian", False),
    ("AQ", "Antarctica", "Antarctica/Casey", 660, 1, "gregorian", False),
    ("AG", "Antigua and Barbuda", "America/Antigua", -240, 0, "gregorian", False),
    ("AR", "Argentina", "America/Argentina/Buenos_Aires", -180, 1, "gregorian", False),
    ("AM", "Armenia", "Asia/Yerevan", 240, 1, "gregorian", False),
    ("AW", "Aruba", "America/Aruba", -240, 1, "gregorian", False),
    ("AU", "Australia", "Antarctica/Macquarie", 660, 1, "gregorian", False),
    ("AT", "Austria", "Europe/Vienna", 60, 1, "gregorian", False),
    ("AZ", "Azerbaijan", "Asia/Baku", 240, 1, "gregorian", False),
    ("BS", "Bahamas", "America/Nassau", -300, 0, "gregorian", False),
    ("BH", "Bahrain", "Asia/Bahrain", 180, 6, "gregorian", True),
    ("BD", "Bangladesh", "Asia/Dhaka", 360, 0, "gregorian", False),
    ("BB", "Barbados", "America/Barbados", -240, 1, "gregorian", False),
    ("BY", "Belarus", "Europe/Minsk", 180, 1, "gregorian", False),
    ("BE", "Belgium", "Europe/Brussels", 60, 1, "gregorian", False),
    ("BZ", "Belize", "America/Belize", -360, 0, "gregorian", False),
    ("BJ", "Benin", "Africa/Porto-Novo", 60, 1, "gregorian", False),
    ("BM", "Bermuda", "Atlantic/Bermuda", -240, 1, "gregorian", False),
    ("BT", "Bhutan", "Asia/Thimphu", 360, 0, "gregorian", False),
    (
        "BO",
        "Bolivia, Plurinational State of",
        "America/La_Paz",
        -240,
        1,
        "gregorian",
        False,
    ),
    (
        "BQ",
        "Bonaire, Sint Eustatius and Saba",
        "America/Kralendijk",
        -240,
        1,
        "gregorian",
        False,
    ),
    ("BA", "Bosnia and Herzegovina", "Europe/Sarajevo", 60, 1, "gregorian", False),
    ("BW", "Botswana", "Africa/Gaborone", 120, 0, "gregorian", False),
    ("BR", "Brazil", "America/Araguaina", -180, 0, "gregorian", False),
    (
        "IO",
        "British Indian Ocean Territory",
        "Indian/Chagos",
        360,
        1,
        "gregorian",
        False,
    ),
    ("BN", "Brunei Darussalam", "Asia/Brunei", 480, 1, "gregorian", False),
    ("BG", "Bulgaria", "Europe/Sofia", 120, 1, "gregorian", False),
    ("BF", "Burkina Faso", "Africa/Ouagadougou", 0, 1, "gregorian", False),
    ("BI", "Burundi", "Africa/Bujumbura", 120, 1, "gregorian", False),
    ("KH", "Cambodia", "Asia/Phnom_Penh", 420, 0, "gregorian", False),
    ("CM", "Cameroon", "Africa/Douala", 60, 1, "gregorian", False),
    ("CA", "Canada", "America/Atikokan", -300, 0, "gregorian", False),
    ("CV", "Cape Verde", "Atlantic/Cape_Verde", -60, 1, "gregorian", False),
    ("KY", "Cayman Islands", "America/Cayman", -300, 1, "gregorian", False),
    ("CF", "Central African Republic", "Africa/Bangui", 60, 1, "gregorian", False),
    ("TD", "Chad", "Africa/Ndjamena", 60, 1, "gregorian", False),
    ("CL", "Chile", "America/Punta_Arenas", -180, 1, "gregorian", False),
    ("CN", "China", "Asia/Shanghai", 480, 1, "gregorian", False),
    ("CX", "Christmas Island", "Indian/Christmas", 420, 1, "gregorian", False),
    ("CC", "Cocos (Keeling) Islands", "Indian/Cocos", 390, 1, "gregorian", True),
    ("CO", "Colombia", "America/Bogota", -300, 0, "gregorian", False),
    ("KM", "Comoros", "Indian/Comoro", 180, 1, "gregorian", True),
    ("CG", "Congo", "Africa/Brazzaville", 60, 1, "gregorian", False),
    (
        "CD",
        "Congo, the Democratic Republic of the",
        "Africa/Kinshasa",
        60,
        1,
        "gregorian",
        False,
    ),
    ("CK", "Cook Islands", "Pacific/Rarotonga", -600, 1, "gregorian", False),
    ("CR", "Costa Rica", "America/Costa_Rica", -360, 1, "gregorian", False),
    ("HR", "Croatia", "Europe/Zagreb", 60, 1, "gregorian", False),
    ("CU", "Cuba", "America/Havana", -300, 1, "gregorian", False),
    ("CW", "Curaçao", "America/Curacao", -240, 1, "gregorian", False),
    ("CY", "Cyprus", "Asia/Famagusta", 120, 1, "gregorian", False),
    ("CZ", "Czech Republic", "Europe/Prague", 60, 1, "gregorian", False),
    ("CI", "Côte d'Ivoire", "Africa/Abidjan", 0, 1, "gregorian", False),
    ("DK", "Denmark", "Europe/Copenhagen", 60, 1, "gregorian", False),
    ("DJ", "Djibouti", "Africa/Djibouti", 180, 6, "gregorian", False),
    ("DM", "Dominica", "America/Dominica", -240, 0, "gregorian", False),
    ("DO", "Dominican Republic", "America/Santo_Domingo", -240, 0, "gregorian", False),
    ("EC", "Ecuador", "America/Guayaquil", -300, 1, "gregorian", False),
    ("EG", "Egypt", "Africa/Cairo", 120, 6, "gregorian", True),
    ("SV", "El Salvador", "America/El_Salvador", -360, 0, "gregorian", False),
    ("GQ", "Equatorial Guinea", "Africa/Malabo", 60, 1, "gregorian", False),
    ("ER", "Eritrea", "Africa/Asmara", 180, 1, "gregorian", False),
    ("EE", "Estonia", "Europe/Tallinn", 120, 1, "gregorian", False),
    ("ET", "Ethiopia", "Africa/Addis_Ababa", 180, 0, "gregorian", False),
    (
        "FK",
        "Falkland Islands (Malvinas)",
        "Atlantic/Stanley",
        -180,
        1,
        "gregorian",
        False,
    ),
    ("FO", "Faroe Islands", "Atlantic/Faroe", 0, 1, "gregorian", False),
    ("FJ", "Fiji", "Pacific/Fiji", 720, 1, "gregorian", False),
    ("FI", "Finland", "Europe/Helsinki", 120, 1, "gregorian", False),
    ("FR", "France", "Europe/Paris", 60, 1, "gregorian", False),
    ("GF", "French Guiana", "America/Cayenne", -180, 1, "gregorian", False),
    ("PF", "French Polynesia", "Pacific/Gambier", -540, 1, "gregorian", False),
    (
        "TF",
        "French Southern Territories",
        "Indian/Kerguelen",
        300,
        1,
        "gregorian",
        False,
    ),
    ("GA", "Gabon", "Africa/Libreville", 60, 1, "gregorian", False),
    ("GM", "Gambia", "Africa/Banjul", 0, 1, "gregorian", False),
    ("GE", "Georgia", "Asia/Tbilisi", 240, 1, "gregorian", False),
    ("DE", "Germany", "Europe/Berlin", 60, 1, "gregorian", False),
    ("GH", "Ghana", "Africa/Accra", 0, 1, "gregorian", False),
    ("GI", "Gibraltar", "Europe/Gibraltar", 60, 1, "gregorian", False),
    ("GR", "Greece", "Europe/Athens", 120, 1, "gregorian", False),
    ("GL", "Greenland", "America/Danmarkshavn", 0, 1, "gregorian", False),
    ("GD", "Grenada", "America/Grenada", -240, 1, "gregorian", False),
    ("GP", "Guadeloupe", "America/Guadeloupe", -240, 1, "gregorian", False),
    ("GU", "Guam", "Pacific/Guam", 600, 0, "gregorian", False),
    ("GT", "Guatemala", "America/Guatemala", -360, 0, "gregorian", False),
    ("GG", "Guernsey", "Europe/Guernsey", 0, 1, "gregorian", False),
    ("GN", "Guinea", "Africa/Conakry", 0, 1, "gregorian", False),
    ("GW", "Guinea-Bissau", "Africa/Bissau", 0, 1, "gregorian", False),
    ("GY", "Guyana", "America/Guyana", -240, 1, "gregorian", False),
    ("HT", "Haiti", "America/Port-au-Prince", -300, 1, "gregorian", False),
    (
        "VA",
        "Holy See (Vatican City State)",
        "Europe/Vatican",
        60,
        1,
        "gregorian",
        False,
    ),
    ("HN", "Honduras", "America/Tegucigalpa", -360, 0, "gregorian", False),
    ("HK", "Hong Kong", "Asia/Hong_Kong", 480, 0, "gregorian", False),
    ("HU", "Hungary", "Europe/Budapest", 60, 1, "gregorian", False),
    ("IS", "Iceland", "Atlantic/Reykjavik", 0, 1, "gregorian", False),
    ("IN", "India", "Asia/Kolkata", 330, 0, "gregorian", False),
    ("ID", "Indonesia", "Asia/Jakarta", 420, 0, "gregorian", False),
    ("IR", "Iran, Islamic Republic of", "Asia/Tehran", 210, 6, "persian", True),
    ("IQ", "Iraq", "Asia/Baghdad", 180, 6, "gregorian", True),
    ("IE", "Ireland", "Europe/Dublin", 0, 1, "gregorian", False),
    ("IM", "Isle of Man", "Europe/Isle_of_Man", 0, 1, "gregorian", False),
    ("IL", "Israel", "Asia/Jerusalem", 120, 0, "gregorian", True),
    ("IT", "Italy", "Europe/Rome", 60, 1, "gregorian", False),
    ("JM", "Jamaica", "America/Jamaica", -300, 0, "gregorian", False),
    ("JP", "Japan", "Asia/Tokyo", 540, 0, "gregorian", False),
    ("JE", "Jersey", "Europe/Jersey", 0, 1, "gregorian", False),
    ("JO", "Jordan", "Asia/Amman", 180, 6, "gregorian", True),
    ("KZ", "Kazakhstan", "Asia/Almaty", 360, 1, "gregorian", False),
    ("KE", "Kenya", "Africa/Nairobi", 180, 0, "gregorian", False),
    ("KI", "Kiribati", "Pacific/Kanton", 780, 1, "gregorian", False),
    (
        "KP",
        "Korea, Democratic People's Republic of",
        "Asia/Pyongyang",
        540,
        1,
        "gregorian",
        False,
    ),
    ("KR", "Korea, Republic of", "Asia/Seoul", 540, 0, "gregorian", False),
    ("KW", "Kuwait", "Asia/Kuwait", 180, 6, "gregorian", True),
    ("KG", "Kyrgyzstan", "Asia/Bishkek", 360, 1, "gregorian", False),
    (
        "LA",
        "Lao People's Democratic Republic",
        "Asia/Vientiane",
        420,
        0,
        "gregorian",
        False,
    ),
    ("LV", "Latvia", "Europe/Riga", 120, 1, "gregorian", False),
    ("LB", "Lebanon", "Asia/Beirut", 120, 1, "gregorian", True),
    ("LS", "Lesotho", "Africa/Maseru", 120, 1, "gregorian", False),
    ("LR", "Liberia", "Africa/Monrovia", 0, 1, "gregorian", False),
    ("LY", "Libya", "Africa/Tripoli", 120, 6, "gregorian", True),
    ("LI", "Liechtenstein", "Europe/Vaduz", 60, 1, "gregorian", False),
    ("LT", "Lithuania", "Europe/Vilnius", 120, 1, "gregorian", False),
    ("LU", "Luxembourg", "Europe/Luxembourg", 60, 1, "gregorian", False),
    ("MO", "Macao", "Asia/Macau", 480, 0, "gregorian", False),
    (
        "MK",
        "Macedonia, the Former Yugoslav Republic of",
        "Europe/Skopje",
        60,
        1,
        "gregorian",
        False,
    ),
    ("MG", "Madagascar", "Indian/Antananarivo", 180, 1, "gregorian", False),
    ("MW", "Malawi", "Africa/Blantyre", 120, 1, "gregorian", False),
    ("MY", "Malaysia", "Asia/Kuala_Lumpur", 480, 1, "gregorian", False),
    ("MV", "Maldives", "Indian/Maldives", 300, 5, "gregorian", True),
    ("ML", "Mali", "Africa/Bamako", 0, 1, "gregorian", False),
    ("MT", "Malta", "Europe/Malta", 60, 0, "gregorian", False),
    ("MH", "Marshall Islands", "Pacific/Kwajalein", 720, 0, "gregorian", False),
    ("MQ", "Martinique", "America/Martinique", -240, 1, "gregorian", False),
    ("MR", "Mauritania", "Africa/Nouakchott", 0, 1, "gregorian", True),
    ("MU", "Mauritius", "Indian/Mauritius", 240, 1, "gregorian", False),
    ("YT", "Mayotte", "Indian/Mayotte", 180, 1, "gregorian", False),
    ("MX", "Mexico", "America/Bahia_Banderas", -360, 0, "gregorian", False),
    (
        "FM",
        "Micronesia, Federated States of",
        "Pacific/Chuuk",
        600,
        1,
        "gregorian",
        False,
    ),
    ("MD", "Moldova, Republic of", "Europe/Chisinau", 120, 1, "gregorian", False),
    ("MC", "Monaco", "Europe/Monaco", 60, 1, "gregorian", False),
    ("MN", "Mongolia", "Asia/Choibalsan", 480, 1, "gregorian", False),
    ("ME", "Montenegro", "Europe/Podgorica", 60, 1, "gregorian", False),
    ("MS", "Montserrat", "America/Montserrat", -240, 1, "gregorian", False),
    ("MA", "Morocco", "Africa/Casablanca", 60, 1, "gregorian", True),
    ("MZ", "Mozambique", "Africa/Maputo", 120, 0, "gregorian", False),
    ("MM", "Myanmar", "Asia/Yangon", 390, 0, "gregorian", False),
    ("NA", "Namibia", "Africa/Windhoek", 120, 1, "gregorian", False),
    ("NR", "Nauru", "Pacific/Nauru", 720, 1, "gregorian", False),
    ("NP", "Nepal", "Asia/Kathmandu", 345, 0, "gregorian", False),
    ("NL", "Netherlands", "Europe/Amsterdam", 60, 1, "gregorian", False),
    ("NC", "New Caledonia", "Pacific/Noumea", 660, 1, "gregorian", False),
    ("NZ", "New Zealand", "Pacific/Auckland", 780, 1, "gregorian", False),
    ("NI", "Nicaragua", "America/Managua", -360, 0, "gregorian", False),
    ("NE", "Niger", "Africa/Niamey", 60, 1, "gregorian", False),
    ("NG", "Nigeria", "Africa/Lagos", 60, 1, "gregorian", False),
    ("NU", "Niue", "Pacific/Niue", -660, 1, "gregorian", False),
    ("NF", "Norfolk Island", "Pacific/Norfolk", 720, 1, "gregorian", False),
    ("MP", "Northern Mariana Islands", "Pacific/Saipan", 600, 1, "gregorian", False),
    ("NO", "Norway", "Europe/Oslo", 60, 1, "gregorian", False),
    ("OM", "Oman", "Asia/Muscat", 240, 6, "gregorian", True),
    ("PK", "Pakistan", "Asia/Karachi", 300, 0, "gregorian", True),
    ("PW", "Palau", "Pacific/Palau", 540, 1, "gregorian", False),
    ("PS", "Palestine, State of", "Asia/Gaza", 120, 1, "gregorian", True),
    ("PA", "Panama", "America/Panama", -300, 0, "gregorian", False),
    ("PG", "Papua New Guinea", "Pacific/Bougainville", 660, 1, "gregorian", False),
    ("PY", "Paraguay", "America/Asuncion", -180, 0, "gregorian", False),
    ("PE", "Peru", "America/Lima", -300, 0, "gregorian", False),
    ("PH", "Philippines", "Asia/Manila", 480, 0, "gregorian", False),
    ("PN", "Pitcairn", "Pacific/Pitcairn", -480, 1, "gregorian", False),
    ("PL", "Poland", "Europe/Warsaw", 60, 1, "gregorian", False),
    ("PT", "Portugal", "Atlantic/Azores", -60, 0, "gregorian", False),
    ("PR", "Puerto Rico", "America/Puerto_Rico", -240, 0, "gregorian", False),
    ("QA", "Qatar", "Asia/Qatar", 180, 6, "gregorian", True),
    ("RO", "Romania", "Europe/Bucharest", 120, 1, "gregorian", False),
    ("RU", "Russian Federation", "Asia/Anadyr", 720, 1, "gregorian", False),
    ("RW", "Rwanda", "Africa/Kigali", 120, 1, "gregorian", False),
    ("RE", "Réunion", "Indian/Reunion", 240, 1, "gregorian", False),
    ("BL", "Saint Barthélemy", "America/St_Barthelemy", -240, 1, "gregorian", False),
    (
        "SH",
        "Saint Helena, Ascension and Tristan da Cunha",
        "Atlantic/St_Helena",
        0,
        1,
        "gregorian",
        False,
    ),
    ("KN", "Saint Kitts and Nevis", "America/St_Kitts", -240, 1, "gregorian", False),
    ("LC", "Saint Lucia", "America/St_Lucia", -240, 1, "gregorian", False),
    (
        "MF",
        "Saint Martin (French part)",
        "America/Marigot",
        -240,
        1,
        "gregorian",
        False,
    ),
    (
        "PM",
        "Saint Pierre and Miquelon",
        "America/Miquelon",
        -180,
        1,
        "gregorian",
        False,
    ),
    (
        "VC",
        "Saint Vincent and the Grenadines",
        "America/St_Vincent",
        -240,
        1,
        "gregorian",
        False,
    ),
    ("WS", "Samoa", "Pacific/Apia", 780, 0, "gregorian", False),
    ("SM", "San Marino", "Europe/San_Marino", 60, 1, "gregorian", False),
    ("ST", "Sao Tome and Principe", "Africa/Sao_Tome", 0, 1, "gregorian", False),
    ("SA", "Saudi Arabia", "Asia/Riyadh", 180, 0, "gregorian", True),
    ("SN", "Senegal", "Africa/Dakar", 0, 1, "gregorian", False),
    ("RS", "Serbia", "Europe/Belgrade", 60, 1, "gregorian", False),
    ("SC", "Seychelles", "Indian/Mahe", 240, 1, "gregorian", False),
    ("SL", "Sierra Leone", "Africa/Freetown", 0, 1, "gregorian", False),
    ("SG", "Singapore", "Asia/Singapore", 480, 0, "gregorian", False),
    (
        "SX",
        "Sint Maarten (Dutch part)",
        "America/Lower_Princes",
        -240,
        1,
        "gregorian",
        False,
    ),
    ("SK", "Slovakia", "Europe/Bratislava", 60, 1, "gregorian", False),
    ("SI", "Slovenia", "Europe/Ljubljana", 60, 1, "gregorian", False),
    ("SB", "Solomon Islands", "Pacific/Guadalcanal", 660, 1, "gregorian", False),
    ("SO", "Somalia", "Africa/Mogadishu", 180, 1, "gregorian", False),
    ("ZA", "South Africa", "Africa/Johannesburg", 120, 0, "gregorian", False),
    (
        "GS",
        "South Georgia and the South Sandwich Islands",
        "Atlantic/South_Georgia",
        -120,
        1,
        "gregorian",
        False,
    ),
    ("SS", "South Sudan", "Africa/Juba", 120, 1, "gregorian", False),
    ("ES", "Spain", "Africa/Ceuta", 60, 1, "gregorian", False),
    ("LK", "Sri Lanka", "Asia/Colombo", 330, 1, "gregorian", False),
    ("SD", "Sudan", "Africa/Khartoum", 120, 6, "gregorian", True),
    ("SR", "Suriname", "America/Paramaribo", -180, 1, "gregorian", False),
    ("SJ", "Svalbard and Jan Mayen", "Arctic/Longyearbyen", 60, 1, "gregorian", False),
    ("SZ", "Swaziland", "Africa/Mbabane", 120, 1, "gregorian", False),
    ("SE", "Sweden", "Europe/Stockholm", 60, 1, "gregorian", False),
    ("CH", "Switzerland", "Europe/Zurich", 60, 1, "gregorian", False),
    ("SY", "Syrian Arab Republic", "Asia/Damascus", 180, 6, "gregorian", True),
    ("TW", "Taiwan, Province of China", "Asia/Taipei", 480, 0, "gregorian", False),
    ("TJ", "Tajikistan", "Asia/Dushanbe", 300, 1, "gregorian", False),
    (
        "TZ",
        "Tanzania, United Republic of",
        "Africa/Dar_es_Salaam",
        180,
        1,
        "gregorian",
        False,
    ),
    ("TH", "Thailand", "Asia/Bangkok", 420, 0, "buddhist", False),
    ("TL", "Timor-Leste", "Asia/Dili", 540, 1, "gregorian", False),
    ("TG", "Togo", "Africa/Lome", 0, 1, "gregorian", False),
    ("TK", "Tokelau", "Pacific/Fakaofo", 780, 1, "gregorian", False),
    ("TO", "Tonga", "Pacific/Tongatapu", 780, 1, "gregorian", False),
    ("TT", "Trinidad and Tobago", "America/Port_of_Spain", -240, 0, "gregorian", False),
    ("TN", "Tunisia", "Africa/Tunis", 60, 1, "gregorian", True),
    ("TR", "Turkey", "Europe/Istanbul", 180, 1, "gregorian", False),
    ("TM", "Turkmenistan", "Asia/Ashgabat", 300, 1, "gregorian", False),
    (
        "TC",
        "Turks and Caicos Islands",
        "America/Grand_Turk",
        -300,
        1,
        "gregorian",
        False,
    ),
    ("TV", "Tuvalu", "Pacific/Funafuti", 720, 1, "gregorian", False),
    ("UG", "Uganda", "Africa/Kampala", 180, 1, "gregorian", False),
    ("UA", "Ukraine", "Europe/Kyiv", 120, 1, "gregorian", False),
    ("AE", "United Arab Emirates", "Asia/Dubai", 240, 6, "gregorian", True),
    ("GB", "United Kingdom", "Europe/London", 0, 0, "gregorian", False),
    ("US", "United States", "America/Adak", -600, 0, "gregorian", False),
    (
        "UM",
        "United States Minor Outlying Islands",
        "Pacific/Midway",
        -660,
        0,
        "gregorian",
        False,
    ),
    ("UY", "Uruguay", "America/Montevideo", -180, 1, "gregorian", False),
    ("UZ", "Uzbekistan", "Asia/Samarkand", 300, 1, "gregorian", False),
    ("VU", "Vanuatu", "Pacific/Efate", 660, 1, "gregorian", False),
    (
        "VE",
        "Venezuela, Bolivarian Republic of",
        "America/Caracas",
        -240,
        0,
        "gregorian",
        False,
    ),
    ("VN", "Viet Nam", "Asia/Ho_Chi_Minh", 420, 1, "gregorian", False),
    ("VG", "Virgin Islands, British", "America/Tortola", -240, 1, "gregorian", False),
    ("VI", "Virgin Islands, U.S.", "America/St_Thomas", -240, 0, "gregorian", False),
    ("WF", "Wallis and Futuna", "Pacific/Wallis", 720, 1, "gregorian", False),
    ("YE", "Yemen", "Asia/Aden", 180, 0, "gregorian", True),
    ("ZM", "Zambia", "Africa/Lusaka", 120, 1, "gregorian", False),
    ("ZW", "Zimbabwe", "Africa/Harare", 120, 0, "gregorian", False),
    ("AX", "Åland Islands", "Europe/Mariehamn", 120, 1, "gregorian", False),
)

COUNTRIES: Mapping[str, CountryTimezone] = MappingProxyType(
    {
        code: CountryTimezone(code, name, timezone, offset, week, calendar, rtl)
        for code, name, timezone, offset, week, calendar, rtl in _COUNTRY_DATA
    }
)


def country(code: str) -> CountryTimezone:
    """Return metadata for an ISO 3166-1 alpha-2 country code.

    Country codes are case-insensitive and surrounding whitespace is ignored.
    ``TypeError`` is raised for non-string values and ``ValueError`` for an
    unknown or malformed country code.
    """
    if not isinstance(code, str):
        raise TypeError("country code must be a string")

    normalized = code.strip().upper()
    if len(normalized) != 2:
        raise ValueError(f"Invalid country code: {code!r}")

    try:
        return COUNTRIES[normalized]
    except KeyError as error:
        raise ValueError(f"Unknown country code: {code!r}") from error


@lru_cache(maxsize=None)
def tzinfo(code: str) -> Timezone:
    """Return an IANA timezone selected by country code.

    Countries spanning multiple timezones use the representative IANA name
    recorded in the bundled country data. Date-aware operations include
    daylight-saving transitions and historical offset changes.
    """
    return country(code).tzinfo
