import sys
import re
import unittest
from datetime import datetime
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parent.parent
PACKAGES_DIR = WORKSPACE / ".packages"
if PACKAGES_DIR.exists():
    sys.path.insert(0, str(PACKAGES_DIR))

from app import app
from vedic_app.astro import calculate_reading, default_form_values
from vedic_app.chara_dasha import (
    build_chara_dasha_rao,
    calculate_antardasha_order,
    calculate_mahadasha_order,
    calculate_mahadasha_years,
    choose_chara_dasha_ruler,
)
from vedic_app.jaimini import calculate_arudhas, calculate_chara_karakas


def build_payload() -> dict[str, str]:
    payload = default_form_values()
    payload.update(
        {
            "birthDate": "1980-12-10",
            "birthTime": "16:14:28",
            "cityName": "Велико Търново",
            "latitudeDegrees": "43",
            "latitudeMinutes": "8",
            "latitudeHemisphere": "N",
            "longitudeDegrees": "25",
            "longitudeMinutes": "42",
            "longitudeHemisphere": "E",
            "timezoneMode": "manual",
            "manualTzSign": "+",
            "manualTzHours": "2",
            "manualTzMinutes": "0",
            "nodeMode": "true",
        }
    )
    return payload


def build_transit_payload() -> dict[str, str]:
    payload = build_payload()
    payload.update(
        {
            "transitDate": "2026-07-15",
            "transitTime": "12:00:00",
            "transitCityName": "София",
            "transitLatitudeDegrees": "42",
            "transitLatitudeMinutes": "42",
            "transitLatitudeHemisphere": "N",
            "transitLongitudeDegrees": "23",
            "transitLongitudeMinutes": "19",
            "transitLongitudeHemisphere": "E",
            "transitTimezoneMode": "manual",
            "transitManualTzSign": "+",
            "transitManualTzHours": "3",
            "transitManualTzMinutes": "0",
            "transitNodeMode": "true",
        }
    )
    return payload


def make_row(key: str, degree_in_sign: float, sign_index: int, house: int) -> dict[str, object]:
    return {
        "key": key,
        "degree_in_sign": degree_in_sign,
        "sign_index": sign_index,
        "sign_number": sign_index + 1,
        "house": house,
    }


def build_full_rows(overrides: dict[str, dict[str, object]] | None = None) -> dict[str, dict[str, object]]:
    rows = {
        "Sun": make_row("Sun", 10.0, 4, 5),
        "Moon": make_row("Moon", 12.0, 3, 4),
        "Mars": make_row("Mars", 18.0, 0, 1),
        "Mercury": make_row("Mercury", 11.0, 2, 3),
        "Jupiter": make_row("Jupiter", 9.0, 8, 9),
        "Venus": make_row("Venus", 13.0, 1, 2),
        "Saturn": make_row("Saturn", 14.0, 9, 10),
        "Rahu": make_row("Rahu", 5.0, 10, 11),
        "Ketu": make_row("Ketu", 5.0, 4, 5),
    }
    if overrides:
        rows.update(overrides)
    return rows


class JaiminiLogicTests(unittest.TestCase):
    def test_chara_karakas_use_deterministic_tiebreak(self) -> None:
        rows = {
            "Sun": make_row("Sun", 29.5, 4, 5),
            "Moon": make_row("Moon", 29.5, 3, 4),
            "Mars": make_row("Mars", 20.0, 0, 1),
            "Mercury": make_row("Mercury", 19.0, 2, 3),
            "Jupiter": make_row("Jupiter", 18.0, 8, 9),
            "Venus": make_row("Venus", 17.0, 1, 2),
            "Saturn": make_row("Saturn", 16.0, 9, 10),
        }

        karakas = calculate_chara_karakas(rows)

        self.assertEqual(
            [row["code"] for row in karakas],
            ["Ат", "Амк", "Бк", "Мк", "Пк", "Гк", "Дк"],
        )
        self.assertEqual(
            [row["planet_key"] for row in karakas],
            ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"],
        )

    def test_arudhas_include_al_and_a1_without_exceptions(self) -> None:
        rows = {
            "Sun": make_row("Sun", 10.0, 4, 5),
            "Moon": make_row("Moon", 10.0, 3, 4),
            "Mars": make_row("Mars", 10.0, 0, 1),
            "Mercury": make_row("Mercury", 10.0, 2, 3),
            "Jupiter": make_row("Jupiter", 10.0, 8, 9),
            "Venus": make_row("Venus", 10.0, 1, 2),
            "Saturn": make_row("Saturn", 10.0, 9, 10),
        }

        arudhas = calculate_arudhas(rows, 0)
        by_code = {row["code"]: row for row in arudhas}

        self.assertIn("Ал", by_code)
        self.assertIn("А1", by_code)
        self.assertEqual(by_code["Ал"]["sign_number"], 1)
        self.assertEqual(by_code["А1"]["sign_number"], 1)

    def test_calculate_reading_adds_jaimini_data(self) -> None:
        result = calculate_reading(build_payload())

        self.assertIn("jaimini", result)
        self.assertEqual(result["jaimini"]["jaimini_chart_payload"]["title"], "Дж")
        self.assertEqual(result["jaimini"]["rashi_card_title"], "Раши")
        self.assertEqual(result["jaimini"]["jaimini_card_title"], "Чара караки и арудхи")
        self.assertEqual(
            [row["code"] for row in result["jaimini"]["chara_karakas"]],
            ["Ат", "Амк", "Бк", "Мк", "Пк", "Гк", "Дк"],
        )
        arudha_codes = [row["code"] for row in result["jaimini"]["arudhas"]]
        self.assertIn("Ал", arudha_codes)
        self.assertIn("А1", arudha_codes)
        self.assertIn("chara_dasha", result["jaimini"])

    def test_jaimini_visual_chart_hides_a1_but_keeps_al_and_red_arudhas(self) -> None:
        result = calculate_reading(build_payload())

        chart_items = [
            item
            for house in result["jaimini"]["jaimini_chart_payload"]["houses"]
            for item in house["items"]
        ]
        chart_svg = result["jaimini"]["jaimini_chart_svg"]

        self.assertIn("Ал", chart_items)
        self.assertNotIn("А1", chart_items)
        self.assertIn("А1", [row["code"] for row in result["jaimini"]["arudhas"]])
        self.assertRegex(
            chart_svg,
            r'class="chart-content chart-content--asc(?: [^"]*)?"[^>]*>Ал</text>',
        )


class CharaDashaLogicTests(unittest.TestCase):
    def test_mahadasha_order_goes_forward_when_ninth_sign_is_direct(self) -> None:
        order, step = calculate_mahadasha_order(2)

        self.assertEqual(step, 1)
        self.assertEqual(order, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1])

    def test_mahadasha_order_goes_backward_when_ninth_sign_is_reverse(self) -> None:
        order, step = calculate_mahadasha_order(0)

        self.assertEqual(step, -1)
        self.assertEqual(order, [0, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1])

    def test_mahadasha_duration_is_twelve_years_when_ruler_is_in_own_sign(self) -> None:
        rows = build_full_rows({"Mars": make_row("Mars", 18.0, 0, 1)})

        self.assertEqual(calculate_mahadasha_years(0, rows), 12)

    def test_choose_ruler_for_scorpio_uses_planet_outside_own_sign(self) -> None:
        rows = build_full_rows(
            {
                "Mars": make_row("Mars", 8.0, 7, 8),
                "Ketu": make_row("Ketu", 14.0, 4, 5),
            }
        )

        ruler = choose_chara_dasha_ruler(7, rows)

        self.assertEqual(ruler["ruler_key"], "Ketu")
        self.assertEqual(ruler["ruler_sign_index"], 4)

    def test_choose_ruler_for_aquarius_uses_more_conjunctions(self) -> None:
        rows = build_full_rows(
            {
                "Saturn": make_row("Saturn", 10.0, 1, 2),
                "Sun": make_row("Sun", 11.0, 1, 2),
                "Moon": make_row("Moon", 12.0, 1, 2),
                "Rahu": make_row("Rahu", 9.0, 2, 3),
            }
        )

        ruler = choose_chara_dasha_ruler(10, rows)

        self.assertEqual(ruler["ruler_key"], "Saturn")
        self.assertEqual(ruler["ruler_sign_index"], 1)

    def test_antardasha_order_for_direct_sign_starts_from_next_sign(self) -> None:
        order, step = calculate_antardasha_order(0)

        self.assertEqual(step, 1)
        self.assertEqual(order, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0])

    def test_antardasha_order_for_reverse_sign_keeps_own_sign_last(self) -> None:
        order, step = calculate_antardasha_order(1)

        self.assertEqual(step, -1)
        self.assertEqual(order, [0, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1])
        self.assertEqual(order[-1], 1)

    def test_chara_dasha_builds_twelve_mahadashas_and_twelve_antardashas(self) -> None:
        rows = build_full_rows()
        result = build_chara_dasha_rao(rows, 0, datetime(1980, 12, 10, 16, 14, 28))

        self.assertEqual(len(result["md_periods"]), 12)
        self.assertTrue(all(len(period["antardashas"]) == 12 for period in result["md_periods"]))
        self.assertEqual(result["md_periods"][0]["start_label"], "10.12.1980, 16:14")
        self.assertEqual(
            result["md_periods"][0]["antardashas"][-1]["sign_name"],
            result["md_periods"][0]["sign_name"],
        )


class JaiminiHtmlTests(unittest.TestCase):
    def test_jaimini_block_is_after_dasha_when_transit_is_hidden(self) -> None:
        client = app.test_client()
        response = client.post("/", data={**build_payload(), "buildMode": "natal"})
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Джаймини", html)
        self.assertIn("Таблица на чара караките", html)
        self.assertIn("Чара даша по Рао", html)
        self.assertIn("Разгъни махадашите и антардашите", html)
        self.assertIn("Период", html)
        self.assertIn("Антардаша", html)
        self.assertIn('data-chart-style-group="jaimini"', html)
        self.assertGreater(html.find("Джаймини"), html.find("Вимшоттари даша"))

    def test_jaimini_block_is_after_transits_when_transit_is_active(self) -> None:
        client = app.test_client()
        response = client.post("/", data={**build_transit_payload(), "buildMode": "transit"})
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Чара даша по Рао", html)
        self.assertGreater(html.find("Джаймини"), html.find("Таблица на транзитите"))
        self.assertLess(html.find("Джаймини"), html.find("Вимшоттари даша"))


if __name__ == "__main__":
    unittest.main()
