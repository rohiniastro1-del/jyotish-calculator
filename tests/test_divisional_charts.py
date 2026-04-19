import sys
import unittest
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parent.parent
PACKAGES_DIR = WORKSPACE / ".packages"
if PACKAGES_DIR.exists():
    sys.path.insert(0, str(PACKAGES_DIR))

from app import app
from vedic_app.astro import calculate_reading, default_form_values
from vedic_app.divisional import (
    DEFAULT_DIVISIONAL_CHART_CODE,
    DIVISIONAL_CHART_BUILDERS,
    DIVISIONAL_CHART_OPTIONS,
    build_divisional_chart_bundle,
)


SUPPORTED_DIVISIONAL_CODES = ["D2", "D3", "D4", "D7", "D9", "D10", "D12", "D24"]


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


class DivisionalChartTests(unittest.TestCase):
    def test_default_selection_is_d9(self) -> None:
        result = calculate_reading(build_payload())

        self.assertEqual(result["selected_divisional_code"], DEFAULT_DIVISIONAL_CHART_CODE)
        self.assertEqual(result["selected_divisional_chart"]["code"], "D9")
        self.assertEqual(result["selected_divisional_chart"]["payload"], result["d9_chart_data"])
        self.assertEqual(result["selected_divisional_chart_svg"], result["d9_chart_svg"])

    def test_registry_contains_supported_divisional_handlers(self) -> None:
        self.assertEqual(list(DIVISIONAL_CHART_BUILDERS.keys()), SUPPORTED_DIVISIONAL_CODES)
        self.assertEqual(
            [option["code"] for option in DIVISIONAL_CHART_OPTIONS],
            SUPPORTED_DIVISIONAL_CODES,
        )

    def test_supported_divisional_chart_is_built_without_placeholder(self) -> None:
        result = calculate_reading(build_payload())
        d2_chart = result["divisional_charts"]["D2"]

        self.assertTrue(d2_chart["implemented"])
        self.assertEqual(d2_chart["card_title"], "D-2 (Hora)")
        self.assertEqual(len(d2_chart["payload"]["houses"]), 12)
        self.assertEqual(d2_chart["payload"]["title"], "D-2")

    def test_unsupported_chart_type_fails_gracefully(self) -> None:
        bundle = build_divisional_chart_bundle(
            "D60",
            build_chart_payload=lambda title, subtitle, asc_sign_index, points, house_key, sign_key, aria_title=None: {
                "title": title,
                "subtitle": subtitle,
                "aria_title": aria_title or title,
                "houses": [],
                "sign_items": {},
            },
            points=[],
        )

        self.assertFalse(bundle["implemented"])
        self.assertEqual(bundle["code"], "D60")
        self.assertEqual(bundle["payload"]["title"], "D-60")

    def test_html_keeps_shared_style_group_and_default_selector(self) -> None:
        client = app.test_client()
        response = client.post("/", data={**build_payload(), "buildMode": "natal"})
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('>Дробни карти</h3>', html)
        self.assertIn('class="divisional-chart-selector"', html)
        self.assertIn('option value="D9" selected', html)
        self.assertEqual(html.count('<article class="chart-card" data-chart-style-group="natal">'), 2)
        self.assertIn('<div class="chart-style-switch" data-chart-style-group="natal"', html)
        self.assertIn('data-default-style="north"', html)


if __name__ == "__main__":
    unittest.main()
