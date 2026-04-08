from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_FLOOR, ROUND_HALF_UP
from pathlib import Path
from threading import RLock

import swisseph as swe
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo

from vedic_app.chart import build_sign_sequence, render_north_chart
from vedic_app.dasha import build_vimshottari_dasha
from vedic_app.data import (
    CITY_LOOKUP,
    NAKSHATRA_NAMES_BG,
    NODE_MODE_LABELS,
    navamsha_sign_index,
    PLANET_LABELS_BG,
    PLANET_NAMES_BG,
    PLANET_ORDER,
    SIGN_NAMES_BG,
)


NAKSHATRA_ARCSECONDS = Decimal("48000")

SWE_BODY_MAP = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
}

FIELD_NAMES = {
    "natal": {
        "date": "birthDate",
        "time": "birthTime",
        "city": "cityName",
        "latitude_degrees": "latitudeDegrees",
        "latitude_minutes": "latitudeMinutes",
        "latitude_hemisphere": "latitudeHemisphere",
        "longitude_degrees": "longitudeDegrees",
        "longitude_minutes": "longitudeMinutes",
        "longitude_hemisphere": "longitudeHemisphere",
        "timezone_mode": "timezoneMode",
        "manual_tz_sign": "manualTzSign",
        "manual_tz_hours": "manualTzHours",
        "manual_tz_minutes": "manualTzMinutes",
        "node_mode": "nodeMode",
    },
    "transit": {
        "date": "transitDate",
        "time": "transitTime",
        "city": "transitCityName",
        "latitude_degrees": "transitLatitudeDegrees",
        "latitude_minutes": "transitLatitudeMinutes",
        "latitude_hemisphere": "transitLatitudeHemisphere",
        "longitude_degrees": "transitLongitudeDegrees",
        "longitude_minutes": "transitLongitudeMinutes",
        "longitude_hemisphere": "transitLongitudeHemisphere",
        "timezone_mode": "transitTimezoneMode",
        "manual_tz_sign": "transitManualTzSign",
        "manual_tz_hours": "transitManualTzHours",
        "manual_tz_minutes": "transitManualTzMinutes",
        "node_mode": "transitNodeMode",
    },
}

TIMEZONE_FINDER = TimezoneFinder()
EPHEMERIS_FILE_PATTERNS = ("*.se1", "*.se2", "*.semo", "*.sepl")
SWE_LOCK = RLock()


class CalculationError(ValueError):
    """Raised when form data cannot be parsed or calculated."""


def _discover_ephemeris_directory() -> Path | None:
    base_dir = Path(__file__).resolve().parent
    candidate_dirs = (
        base_dir / "ephe",
        base_dir.parent / "ephe",
        base_dir.parent / ".ephe",
    )
    for candidate in candidate_dirs:
        if not candidate.is_dir():
            continue
        if any(candidate.glob(pattern) for pattern in EPHEMERIS_FILE_PATTERNS):
            return candidate
    return None


def _configure_ephemeris() -> str | None:
    directory = _discover_ephemeris_directory()
    if directory is not None:
        swe.set_ephe_path(str(directory))
        return str(directory)
    return None


EPHEMERIS_DIRECTORY = _configure_ephemeris()


def default_form_values() -> dict[str, str]:
    now_local = datetime.now(ZoneInfo("Europe/Sofia"))
    values: dict[str, str] = {}
    values.update(_default_chart_form_values("natal", "София"))
    values.update(
        _default_chart_form_values(
            "transit",
            "София",
            date_value=now_local.strftime("%Y-%m-%d"),
            time_value=now_local.strftime("%H:%M:%S"),
        )
    )
    return values


def _default_chart_form_values(
    prefix: str,
    city_name: str,
    date_value: str = "",
    time_value: str = "",
) -> dict[str, str]:
    city = CITY_LOOKUP[city_name]
    lat_deg, lat_min = decimal_to_degree_minutes(city["lat"])
    lon_deg, lon_min = decimal_to_degree_minutes(city["lon"])
    names = FIELD_NAMES[prefix]
    return {
        names["date"]: date_value,
        names["time"]: time_value,
        names["city"]: city_name,
        names["latitude_degrees"]: str(lat_deg),
        names["latitude_minutes"]: str(lat_min),
        names["latitude_hemisphere"]: "N",
        names["longitude_degrees"]: str(lon_deg),
        names["longitude_minutes"]: str(lon_min),
        names["longitude_hemisphere"]: "E",
        names["timezone_mode"]: "auto",
        names["manual_tz_sign"]: "+",
        names["manual_tz_hours"]: "2",
        names["manual_tz_minutes"]: "0",
        names["node_mode"]: "true",
    }


def decimal_to_degree_minutes(value: float) -> tuple[int, int]:
    absolute = abs(value)
    degrees = int(absolute)
    minutes = int(round((absolute - degrees) * 60))
    if minutes == 60:
        degrees += 1
        minutes = 0
    return degrees, minutes


def _format_coordinate_label(latitude: float, longitude: float) -> str:
    lat_deg, lat_min = decimal_to_degree_minutes(latitude)
    lon_deg, lon_min = decimal_to_degree_minutes(longitude)
    lat_hemi = "N" if latitude >= 0 else "S"
    lon_hemi = "E" if longitude >= 0 else "W"
    return (
        f"{lat_deg:02d}° {lat_min:02d}' {lat_hemi}, "
        f"{lon_deg:02d}° {lon_min:02d}' {lon_hemi} "
        f"({latitude:.4f}°, {longitude:.4f}°)"
    )


def _field_name(prefix: str, key: str) -> str:
    return FIELD_NAMES[prefix][key]


def _get_form_value(form_data: dict[str, str], prefix: str, key: str) -> str:
    return form_data.get(_field_name(prefix, key), "").strip()


def _normalize_degrees(value: float) -> float:
    normalized = value % 360.0
    return 0.0 if normalized == 360.0 else normalized


def _to_decimal(value: float) -> Decimal:
    return Decimal(str(value))


def _degree_fraction_to_dms(value: float) -> tuple[int, int, int]:
    total_arcseconds = int(
        (_to_decimal(value) * Decimal("3600")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    )
    max_arcseconds = 30 * 3600 - 1
    total_arcseconds = min(total_arcseconds, max_arcseconds)
    degrees, remainder = divmod(total_arcseconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return degrees, minutes, seconds


def _format_dms(value: float) -> str:
    degrees, minutes, seconds = _degree_fraction_to_dms(value)
    return f"{degrees:02d}° {minutes:02d}' {seconds:02d}\""


def _full_degree_dms(value: float) -> str:
    normalized = _normalize_degrees(value)
    total_arcseconds = int(
        (_to_decimal(normalized) * Decimal("3600")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    )
    if total_arcseconds >= 360 * 3600:
        total_arcseconds = 0
    degrees, remainder = divmod(total_arcseconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{degrees:03d}° {minutes:02d}' {seconds:02d}\""


def _zodiac_details(longitude: float) -> dict[str, object]:
    normalized = _normalize_degrees(longitude)
    sign_index = int(normalized // 30)
    degree_in_sign = normalized - (sign_index * 30)
    total_arcseconds = _to_decimal(normalized) * Decimal("3600")
    nak_index = int((total_arcseconds // NAKSHATRA_ARCSECONDS).to_integral_value(rounding=ROUND_FLOOR))
    nak_offset = total_arcseconds % NAKSHATRA_ARCSECONDS
    pada = int((nak_offset / Decimal("12000")).to_integral_value(rounding=ROUND_FLOOR)) + 1
    return {
        "longitude": normalized,
        "sign_index": sign_index,
        "sign_number": sign_index + 1,
        "sign_name": SIGN_NAMES_BG[sign_index],
        "degree_in_sign": degree_in_sign,
        "degree_dms": _format_dms(degree_in_sign),
        "nakshatra": NAKSHATRA_NAMES_BG[nak_index],
        "pada": pada,
    }


def _navamsha_sign(sign_index: int, degree_in_sign: float) -> int:
    return navamsha_sign_index(sign_index, degree_in_sign)


def _dms_to_decimal(degrees_text: str, minutes_text: str, hemisphere: str, axis: str) -> float:
    try:
        degrees = int(degrees_text)
        minutes = int(minutes_text)
    except ValueError as exc:
        raise CalculationError("Координатите трябва да са цели числа в градуси и минути.") from exc

    if minutes < 0 or minutes >= 60:
        raise CalculationError("Минутите в координатите трябва да са между 0 и 59.")

    limit = 90 if axis == "lat" else 180
    if degrees < 0 or degrees > limit:
        axis_label = "ширина" if axis == "lat" else "дължина"
        raise CalculationError(f"Градусите по {axis_label} трябва да са между 0 и {limit}.")

    value = degrees + (minutes / 60)
    if hemisphere in {"S", "W"}:
        value *= -1
    return value


def _parse_manual_offset(sign_text: str, hours_text: str, minutes_text: str) -> int:
    try:
        hours = int(hours_text)
        minutes = int(minutes_text)
    except ValueError as exc:
        raise CalculationError("Ръчната часова зона трябва да е в цели часове и минути.") from exc

    if hours < 0 or hours > 14 or minutes < 0 or minutes >= 60:
        raise CalculationError("Ръчната часова зона е извън позволения диапазон.")

    total = hours * 60 + minutes
    return -total if sign_text == "-" else total


def _format_utc_offset(total_minutes: int) -> str:
    sign = "+" if total_minutes >= 0 else "-"
    absolute = abs(total_minutes)
    hours, minutes = divmod(absolute, 60)
    return f"UTC{sign}{hours:02d}:{minutes:02d}"


def _local_roundtrip_matches(local_candidate: datetime, naive_local: datetime, tz_info: ZoneInfo) -> bool:
    roundtrip = local_candidate.astimezone(timezone.utc).astimezone(tz_info).replace(tzinfo=None)
    return roundtrip == naive_local


def _resolve_auto_local_datetime(
    naive_local: datetime,
    tz_info: ZoneInfo,
) -> tuple[datetime, str | None]:
    early = naive_local.replace(tzinfo=tz_info, fold=0)
    late = naive_local.replace(tzinfo=tz_info, fold=1)

    early_valid = _local_roundtrip_matches(early, naive_local, tz_info)
    late_valid = _local_roundtrip_matches(late, naive_local, tz_info)

    if early_valid and late_valid:
        if early.utcoffset() != late.utcoffset():
            return early, (
                "Часът попада в двусмислен момент около смяна на лятно/зимно време. "
                "Автоматично е избран по-ранният валиден локален час; при нужда коригирай зоната ръчно."
            )
        return early, None

    if early_valid:
        return early, None

    if late_valid:
        return late, (
            "Часът е разрешен по късния DST вариант; при нужда коригирай зоната ръчно."
        )

    raise CalculationError(
        "Автоматичното определяне на часовата зона попадна в невалиден локален час "
        "около смяна на лятно/зимно време. Задай часовата зона ръчно за тази карта."
    )


def _resolve_timezone(
    date_text: str,
    time_text: str,
    latitude: float,
    longitude: float,
    timezone_mode: str,
    manual_offset_minutes: int,
    preferred_timezone: str | None,
) -> tuple[datetime, datetime, dict[str, str]]:
    try:
        naive_local = datetime.fromisoformat(f"{date_text}T{time_text}")
    except ValueError as exc:
        raise CalculationError("Датата и часът трябва да са попълнени коректно.") from exc

    if timezone_mode == "manual":
        tz_info = timezone(timedelta(minutes=manual_offset_minutes))
        aware_local = naive_local.replace(tzinfo=tz_info)
        offset_label = _format_utc_offset(manual_offset_minutes)
        timezone_summary = {
            "mode": "Ръчно",
            "name": offset_label,
            "offset_label": offset_label,
            "source": "Ръчно въведена часова зона.",
        }
    else:
        timezone_name = TIMEZONE_FINDER.timezone_at(lat=latitude, lng=longitude) or preferred_timezone
        if not timezone_name:
            timezone_name = "Europe/Sofia"
        tz_info = ZoneInfo(timezone_name)
        aware_local, note = _resolve_auto_local_datetime(naive_local, tz_info)
        offset_minutes = int((aware_local.utcoffset() or timedelta()).total_seconds() // 60)
        timezone_summary = {
            "mode": "Автоматично",
            "name": timezone_name,
            "offset_label": _format_utc_offset(offset_minutes),
            "source": (
                "Часовата зона е определена по координати и историческите правила за датата."
                if not note
                else f"Часовата зона е определена по координати и историческите правила за датата. {note}"
            ),
        }

    aware_utc = aware_local.astimezone(timezone.utc)
    return aware_local, aware_utc, timezone_summary


def _julian_day(aware_utc: datetime) -> float:
    hour_fraction = (
        aware_utc.hour
        + (aware_utc.minute / 60)
        + (aware_utc.second / 3600)
        + (aware_utc.microsecond / 3_600_000_000)
    )
    return swe.julday(aware_utc.year, aware_utc.month, aware_utc.day, hour_fraction)


def _traditional_sidereal_ascendant(jd_ut: float, latitude: float, longitude: float) -> tuple[float, float]:
    # JHora-style lagna matches better when we take the tropical ascendant
    # and subtract the selected ayanamsha, instead of relying on direct
    # sidereal house output from Swiss Ephemeris.
    ayanamsha = swe.get_ayanamsa_ut(jd_ut)
    _, ascmc_tropical = swe.houses_ex(jd_ut, latitude, longitude, b"P", 0)
    asc_longitude = _normalize_degrees(ascmc_tropical[0] - ayanamsha)
    return asc_longitude, ayanamsha


def _planet_chart_code(key: str, retrograde: bool) -> str:
    label = PLANET_LABELS_BG[key]
    return f"({label})" if retrograde else label


def _ephemeris_source_summary(retflags: list[int]) -> dict[str, str]:
    if retflags and all(flag & swe.FLG_SWIEPH for flag in retflags):
        detail = "Използват се файловете на Swiss Ephemeris."
        if EPHEMERIS_DIRECTORY:
            detail = f"{detail} Път: {EPHEMERIS_DIRECTORY}"
        return {"label": "Swiss Ephemeris", "detail": detail}

    if any(flag & swe.FLG_MOSEPH for flag in retflags):
        return {
            "label": "Moshier fallback",
            "detail": (
                "Липсват Swiss Ephemeris файлове (*.se1), затова изчисленията в момента ползват "
                "Moshier fallback и могат да се разминават с JHora с няколко до десетки ъглови секунди."
            ),
        }

    if any(flag & swe.FLG_JPLEPH for flag in retflags):
        return {"label": "JPL ephemeris", "detail": "Използва се JPL ephemeris източник."}

    return {
        "label": "Неуточнен източник",
        "detail": "Източникът на епхемеридите не можа да бъде определен еднозначно.",
    }


def _build_chart_payload(
    title: str,
    subtitle: str,
    asc_sign_index: int,
    points: list[dict[str, object]],
    house_key: str,
    aria_title: str | None = None,
) -> dict[str, object]:
    sign_sequence = build_sign_sequence(asc_sign_index + 1)
    houses = []
    for house_number in range(1, 13):
        sign_number = sign_sequence[house_number]
        items = [point["chart_code"] for point in points if point[house_key] == house_number]
        houses.append({"house": house_number, "sign_number": sign_number, "items": items})
    return {
        "title": title,
        "subtitle": subtitle,
        "aria_title": aria_title or title,
        "houses": houses,
    }


def _calculate_chart(
    form_data: dict[str, str],
    prefix: str,
    d1_subtitle: str,
    include_d9: bool,
) -> dict[str, object]:
    date_text = _get_form_value(form_data, prefix, "date")
    time_text = _get_form_value(form_data, prefix, "time")
    if not date_text or not time_text:
        chart_label = "рождената" if prefix == "natal" else "транзитната"
        raise CalculationError(f"Въведи дата и точен час за {chart_label} карта.")

    city_name = _get_form_value(form_data, prefix, "city")
    city = CITY_LOOKUP.get(city_name) if city_name else None

    latitude = _dms_to_decimal(
        _get_form_value(form_data, prefix, "latitude_degrees"),
        _get_form_value(form_data, prefix, "latitude_minutes"),
        _get_form_value(form_data, prefix, "latitude_hemisphere") or "N",
        "lat",
    )
    longitude = _dms_to_decimal(
        _get_form_value(form_data, prefix, "longitude_degrees"),
        _get_form_value(form_data, prefix, "longitude_minutes"),
        _get_form_value(form_data, prefix, "longitude_hemisphere") or "E",
        "lon",
    )
    manual_offset_minutes = _parse_manual_offset(
        _get_form_value(form_data, prefix, "manual_tz_sign") or "+",
        _get_form_value(form_data, prefix, "manual_tz_hours") or "0",
        _get_form_value(form_data, prefix, "manual_tz_minutes") or "0",
    )

    timezone_mode = _get_form_value(form_data, prefix, "timezone_mode") or "auto"
    preferred_timezone = city["timezone"] if city else None
    local_dt, utc_dt, timezone_summary = _resolve_timezone(
        date_text,
        time_text,
        latitude,
        longitude,
        timezone_mode,
        manual_offset_minutes,
        preferred_timezone,
    )

    with SWE_LOCK:
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        jd_ut = _julian_day(utc_dt)
        # JHora-style longitude tables match Swiss Ephemeris best when using
        # true geocentric positions instead of apparent positions.
        flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_TRUEPOS
        node_mode = _get_form_value(form_data, prefix, "node_mode") or "true"
        node_id = swe.TRUE_NODE if node_mode == "true" else swe.MEAN_NODE

        asc_longitude, ayanamsha = _traditional_sidereal_ascendant(jd_ut, latitude, longitude)
        asc_details = _zodiac_details(asc_longitude)
        asc_nav_sign = _navamsha_sign(asc_details["sign_index"], asc_details["degree_in_sign"])

        points: list[dict[str, object]] = []
        rows_by_key: dict[str, dict[str, object]] = {}
        ephemeris_flags: list[int] = []

        asc_row = {
            "key": "Ascendant",
            "name": PLANET_NAMES_BG["Ascendant"],
            "label": PLANET_LABELS_BG["Ascendant"],
            "retrograde": False,
            **asc_details,
        }
        asc_row["house"] = 1
        asc_row["nav_house"] = 1
        asc_row["nav_sign_name"] = SIGN_NAMES_BG[asc_nav_sign]
        asc_row["chart_code"] = PLANET_LABELS_BG["Ascendant"]
        points.append(asc_row)
        rows_by_key["Ascendant"] = asc_row

        for key in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
            values, retflags = swe.calc_ut(jd_ut, SWE_BODY_MAP[key], flags)
            ephemeris_flags.append(retflags)
            longitude_value = _normalize_degrees(values[0])
            speed = values[3]
            details = _zodiac_details(longitude_value)
            nav_sign_index = _navamsha_sign(details["sign_index"], details["degree_in_sign"])
            row = {
                "key": key,
                "name": PLANET_NAMES_BG[key],
                "label": PLANET_LABELS_BG[key],
                "retrograde": speed < 0,
                **details,
            }
            row["house"] = ((row["sign_index"] - asc_details["sign_index"]) % 12) + 1
            row["nav_house"] = ((nav_sign_index - asc_nav_sign) % 12) + 1
            row["nav_sign_name"] = SIGN_NAMES_BG[nav_sign_index]
            row["chart_code"] = _planet_chart_code(key, row["retrograde"])
            points.append(row)
            rows_by_key[key] = row

        rahu_values, rahu_retflags = swe.calc_ut(jd_ut, node_id, flags)
        ephemeris_flags.append(rahu_retflags)
        rahu_longitude = _normalize_degrees(rahu_values[0])
        rahu_speed = rahu_values[3]
        rahu_details = _zodiac_details(rahu_longitude)
        rahu_nav_sign = _navamsha_sign(rahu_details["sign_index"], rahu_details["degree_in_sign"])
        rahu_row = {
            "key": "Rahu",
            "name": PLANET_NAMES_BG["Rahu"],
            "label": PLANET_LABELS_BG["Rahu"],
            "retrograde": rahu_speed < 0,
            **rahu_details,
        }
        rahu_row["house"] = ((rahu_row["sign_index"] - asc_details["sign_index"]) % 12) + 1
        rahu_row["nav_house"] = ((rahu_nav_sign - asc_nav_sign) % 12) + 1
        rahu_row["nav_sign_name"] = SIGN_NAMES_BG[rahu_nav_sign]
        rahu_row["chart_code"] = _planet_chart_code("Rahu", rahu_row["retrograde"])
        points.append(rahu_row)
        rows_by_key["Rahu"] = rahu_row

        ketu_longitude = _normalize_degrees(rahu_longitude + 180)
        ketu_details = _zodiac_details(ketu_longitude)
        ketu_nav_sign = _navamsha_sign(ketu_details["sign_index"], ketu_details["degree_in_sign"])
        ketu_row = {
            "key": "Ketu",
            "name": PLANET_NAMES_BG["Ketu"],
            "label": PLANET_LABELS_BG["Ketu"],
            "retrograde": True,
            **ketu_details,
        }
        ketu_row["house"] = ((ketu_row["sign_index"] - asc_details["sign_index"]) % 12) + 1
        ketu_row["nav_house"] = ((ketu_nav_sign - asc_nav_sign) % 12) + 1
        ketu_row["nav_sign_name"] = SIGN_NAMES_BG[ketu_nav_sign]
        ketu_row["chart_code"] = _planet_chart_code("Ketu", ketu_row["retrograde"])
        points.append(ketu_row)
        rows_by_key["Ketu"] = ketu_row

    order_index = {key: index for index, key in enumerate(PLANET_ORDER)}
    points_by_order = sorted(points, key=lambda point: order_index[point["key"]])

    d1_title = "\u0422\u0420" if prefix == "transit" else "D-1"
    d1_aria_title = "D-1 (\u0422\u0440\u0430\u043d\u0437\u0438\u0442\u0438)" if prefix == "transit" else "D-1"
    d1_chart = _build_chart_payload(
        d1_title,
        d1_subtitle,
        asc_details["sign_index"],
        points_by_order,
        "house",
        aria_title=d1_aria_title,
    )
    d9_chart_svg = None
    if include_d9:
        d9_chart = _build_chart_payload("D-9", "Навамша", asc_nav_sign, points_by_order, "nav_house")
        d9_chart_svg = render_north_chart(d9_chart)

    table_rows = []
    for row in sorted(rows_by_key.values(), key=lambda item: order_index[item["key"]]):
        table_rows.append(
            {
                "name": row["name"],
                "label": row["label"],
                "sign_name": row["sign_name"],
                "sign_number": row["sign_number"],
                "degree_dms": row["degree_dms"],
                "nakshatra": row["nakshatra"],
                "pada": row["pada"],
                "retrograde": row["retrograde"],
                "house": row["house"],
                "nav_sign_name": row["nav_sign_name"],
            }
        )

    ephemeris_source = _ephemeris_source_summary(ephemeris_flags)

    return {
        "local_birth_label": local_dt.strftime("%d.%m.%Y %H:%M:%S"),
        "utc_birth_label": utc_dt.strftime("%d.%m.%Y %H:%M:%S UTC"),
        "timezone": timezone_summary,
        "location_label": city_name or "Ръчно въведено място",
        "coordinates_label": _format_coordinate_label(latitude, longitude),
        "ayanamsha_label": _full_degree_dms(ayanamsha),
        "node_mode_label": NODE_MODE_LABELS[node_mode],
        "ephemeris_source": ephemeris_source,
        "lagna": {
            "sign_name": asc_details["sign_name"],
            "sign_number": asc_details["sign_number"],
            "degree_dms": asc_details["degree_dms"],
            "nakshatra": asc_details["nakshatra"],
            "pada": asc_details["pada"],
            "nav_sign_name": SIGN_NAMES_BG[asc_nav_sign],
        },
        "d1_chart_data": d1_chart,
        "d1_chart_svg": render_north_chart(d1_chart),
        "d9_chart_data": d9_chart if include_d9 else None,
        "d9_chart_svg": d9_chart_svg,
        "table_rows": table_rows,
        "raw_rows": rows_by_key,
        "asc_sign_index": asc_details["sign_index"],
        "moon_longitude": rows_by_key["Moon"]["longitude"],
        "local_datetime": local_dt,
    }


def calculate_reading(form_data: dict[str, str], build_mode: str = "natal") -> dict[str, object]:
    natal = _calculate_chart(form_data, "natal", "Раши", include_d9=True)

    dasha = build_vimshottari_dasha(natal["moon_longitude"], natal["local_datetime"])

    transit_date = _get_form_value(form_data, "transit", "date")
    transit_time = _get_form_value(form_data, "transit", "time")
    if build_mode == "transit" and (bool(transit_date) ^ bool(transit_time)):
        raise CalculationError("За транзитната карта попълни и дата, и час, или остави и двете празни.")

    transit = None
    if build_mode == "transit":
        if not transit_date or not transit_time:
            raise CalculationError("За транзитната карта попълни дата, час и място, а след това натисни бутона за транзити.")
        transit = _calculate_chart(form_data, "transit", "Транзити", include_d9=False)

    return {
        "local_birth_label": natal["local_birth_label"],
        "utc_birth_label": natal["utc_birth_label"],
        "timezone": natal["timezone"],
        "location_label": natal["location_label"],
        "coordinates_label": natal["coordinates_label"],
        "ayanamsha_label": natal["ayanamsha_label"],
        "node_mode_label": natal["node_mode_label"],
        "ephemeris_source": natal["ephemeris_source"],
        "lagna": natal["lagna"],
        "d1_chart_data": natal["d1_chart_data"],
        "d1_chart_svg": natal["d1_chart_svg"],
        "d9_chart_data": natal["d9_chart_data"],
        "d9_chart_svg": natal["d9_chart_svg"],
        "table_rows": natal["table_rows"],
        "dasha": dasha,
        "transit": transit,
    }
