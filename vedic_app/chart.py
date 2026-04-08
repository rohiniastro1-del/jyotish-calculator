from __future__ import annotations

from html import escape


# In the North Indian chart the houses are fixed. Once Lagna is placed in the
# top diamond (house 1), the signs must continue sequentially counterclockwise:
# 1 -> 2 -> 3 -> ... -> 12, wrapping after Pisces back to Aries.
COUNTERCLOCKWISE_HOUSE_SEQUENCE = (
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
)

HOUSE_LAYOUTS = {
    1: {"sign": (286.0, 221.0), "box": {"x": 240.0, "y": 99.0, "width": 86.0, "height": 74.0}},
    2: {"sign": (149.0, 108.0), "box": {"x": 106.0, "y": 16.0, "width": 86.0, "height": 74.0}},
    3: {"sign": (117.0, 136.0), "box": {"x": 14.0, "y": 99.0, "width": 86.0, "height": 74.0}},
    4: {"sign": (241.0, 266.0), "box": {"x": 93.0, "y": 221.0, "width": 86.0, "height": 75.0}},
    5: {"sign": (117.0, 395.0), "box": {"x": 14.0, "y": 357.0, "width": 86.0, "height": 74.0}},
    6: {"sign": (149.0, 423.0), "box": {"x": 101.0, "y": 441.0, "width": 86.0, "height": 74.0}},
    7: {"sign": (286.0, 310.0), "box": {"x": 240.0, "y": 366.0, "width": 86.0, "height": 74.0}},
    8: {"sign": (423.0, 423.0), "box": {"x": 383.0, "y": 441.0, "width": 87.0, "height": 74.0}},
    9: {"sign": (455.0, 395.0), "box": {"x": 476.0, "y": 366.0, "width": 86.0, "height": 74.0}},
    10: {"sign": (331.0, 266.0), "box": {"x": 371.0, "y": 221.0, "width": 86.0, "height": 75.0}},
    11: {"sign": (455.0, 136.0), "box": {"x": 476.0, "y": 99.0, "width": 86.0, "height": 74.0}},
    12: {"sign": (423.0, 108.0), "box": {"x": 383.0, "y": 16.0, "width": 87.0, "height": 74.0}},
}


def build_sign_sequence(lagna_sign_number: int) -> dict[int, int]:
    normalized_lagna = ((lagna_sign_number - 1) % 12) + 1
    return {
        house_number: ((normalized_lagna + offset - 1) % 12) + 1
        for offset, house_number in enumerate(COUNTERCLOCKWISE_HOUSE_SEQUENCE)
    }


def _group_items(items: list[str]) -> list[list[str]]:
    count = len(items)
    if count == 0:
        return []
    if count == 1:
        return [items]
    if count in (2, 3, 4):
        return [[item] for item in items]
    if count == 5:
        return [items[:2], items[2:4], items[4:]]
    return [items[index:index + 2] for index in range(0, count, 2)]


def _line_y_positions(box: dict[str, float], line_count: int) -> list[float]:
    center_y = box["y"] + (box["height"] / 2)
    if line_count <= 3:
        line_gap = 20.0
    elif line_count == 4:
        line_gap = 18.0
    else:
        line_gap = 16.0
    first_y = center_y - ((line_count - 1) * line_gap / 2)
    return [first_y + (index * line_gap) for index in range(line_count)]


def _line_x_positions(box: dict[str, float], item_count: int) -> list[float]:
    center_x = box["x"] + (box["width"] / 2)
    if item_count == 1:
        return [center_x]

    spread = min(20.0, box["width"] * 0.22)
    return [center_x - spread, center_x + spread]


def _item_positions(house_number: int, items: list[str]) -> list[tuple[str, float, float]]:
    box = HOUSE_LAYOUTS[house_number]["box"]
    groups = _group_items(items)
    y_positions = _line_y_positions(box, len(groups))

    placed: list[tuple[str, float, float]] = []
    for group, y_pos in zip(groups, y_positions):
        for item, x_pos in zip(group, _line_x_positions(box, len(group))):
            placed.append((item, x_pos, y_pos))
    return placed


def _line_positions(house_number: int, items: list[str]) -> list[tuple[str, float, float]]:
    box = HOUSE_LAYOUTS[house_number]["box"]
    groups = _group_items(items)
    center_x = box["x"] + (box["width"] / 2)
    y_positions = _line_y_positions(box, len(groups))
    return [(" ".join(group), center_x, y_pos) for group, y_pos in zip(groups, y_positions)]


def _text_class(item: str, line_count: int) -> str:
    class_names = ["chart-content"]
    if item in {"Ас", "Àñ"}:
        class_names.append("chart-content--asc")
    elif "(" in item:
        class_names.append("chart-content--retro")
    if line_count >= 5:
        class_names.append("chart-content--tight")
    return " ".join(class_names)


def _sign_class(sign_number: object) -> str:
    class_names = ["chart-sign-label"]
    if len(str(sign_number)) >= 2:
        class_names.append("chart-sign-label--double")
    return " ".join(class_names)


def render_north_chart(chart: dict[str, object]) -> str:
    title = escape(str(chart["title"]))
    subtitle = escape(str(chart["subtitle"]))
    aria_title = escape(str(chart.get("aria_title", chart["title"])))
    chart_id = "".join(
        character.lower()
        for character in f"{chart['title']}-{chart['subtitle']}"
        if character.isascii() and character.isalnum()
    ) or "chart"
    bg_id = f"chartBg-{chart_id}"
    center_id = f"centerGlow-{chart_id}"
    line_mask_id = f"lineMask-{chart_id}"

    sign_parts: list[str] = []
    item_parts: list[str] = []

    for house in chart["houses"]:
        house_number = house["house"]
        sign_x, sign_y = HOUSE_LAYOUTS[house_number]["sign"]
        sign_parts.append(
            f'<text class="{_sign_class(house["sign_number"])}" x="{sign_x:.1f}" y="{sign_y:.1f}" '
            f'text-anchor="middle" dominant-baseline="middle">{house["sign_number"]}</text>'
        )

        items = house["items"]
        line_count = len(_group_items(items))
        for item, x_pos, y_pos in _item_positions(house_number, items):
            item_parts.append(
                f'<text class="{_text_class(item, line_count)}" x="{x_pos:.1f}" y="{y_pos:.1f}" '
                f'text-anchor="middle" dominant-baseline="middle">{escape(item)}</text>'
            )

    return f"""
<svg class="north-chart-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 572 531" role="img" aria-label="{aria_title}">
  <defs>
    <linearGradient id="{bg_id}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fffef9" />
      <stop offset="100%" stop-color="#f4eedb" />
    </linearGradient>
    <linearGradient id="{center_id}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ddd2a5" />
      <stop offset="100%" stop-color="#c5b175" />
    </linearGradient>
    <mask id="{line_mask_id}">
      <rect width="572" height="531" fill="white" />
      <rect x="254" y="234" width="64" height="64" rx="16" fill="black" />
    </mask>
  </defs>
  <rect width="572" height="531" rx="18" fill="url(#{bg_id})" />
  <g mask="url(#{line_mask_id})">
    <rect x="9" y="10" width="554" height="511" fill="none" stroke="#4e7b4a" stroke-width="2"/>
    <line x1="286" y1="10" x2="563" y2="265.5" stroke="#4e7b4a" stroke-width="2"/>
    <line x1="563" y1="265.5" x2="286" y2="521" stroke="#4e7b4a" stroke-width="2"/>
    <line x1="286" y1="521" x2="9" y2="265.5" stroke="#4e7b4a" stroke-width="2"/>
    <line x1="9" y1="265.5" x2="286" y2="10" stroke="#4e7b4a" stroke-width="2"/>
    <line x1="9" y1="10" x2="147.5" y2="137.75" stroke="#4e7b4a" stroke-width="2"/>
    <line x1="147.5" y1="137.75" x2="311" y2="291" stroke="#4e7b4a" stroke-width="2"/>
    <line x1="563" y1="10" x2="424.5" y2="137.75" stroke="#4e7b4a" stroke-width="2"/>
    <line x1="424.5" y1="137.75" x2="260" y2="291" stroke="#4e7b4a" stroke-width="2"/>
    <line x1="9" y1="521" x2="147.5" y2="393.25" stroke="#4e7b4a" stroke-width="2"/>
    <line x1="147.5" y1="393.25" x2="311" y2="240" stroke="#4e7b4a" stroke-width="2"/>
    <line x1="563" y1="521" x2="424.5" y2="393.25" stroke="#4e7b4a" stroke-width="2"/>
    <line x1="424.5" y1="393.25" x2="260" y2="240" stroke="#4e7b4a" stroke-width="2"/>
  </g>
  <rect x="260" y="240" width="51" height="51" rx="10" fill="url(#{center_id})" stroke="#4e7b4a" stroke-width="2"/>
  <text x="286" y="272" text-anchor="middle" class="chart-center-title">{title}</text>
  {"".join(sign_parts)}
  {"".join(item_parts)}
</svg>
""".strip()
