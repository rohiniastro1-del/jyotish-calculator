from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path


SIGN_NAMES_BG = [
    "Овен",
    "Телец",
    "Близнаци",
    "Рак",
    "Лъв",
    "Дева",
    "Везни",
    "Скорпион",
    "Стрелец",
    "Козирог",
    "Водолей",
    "Риби",
]

NAKSHATRA_NAMES_BG = [
    "Ашвини",
    "Бхарани",
    "Криттика",
    "Рохини",
    "Мригашира",
    "Ардра",
    "Пунарвасу",
    "Пушя",
    "Ашлеша",
    "Мага",
    "Пурва Пхалгуни",
    "Утара Пхалгуни",
    "Хаста",
    "Читра",
    "Свати",
    "Вишакха",
    "Анурадха",
    "Джйештха",
    "Мула",
    "Пурва Ашадха",
    "Утара Ашадха",
    "Шравана",
    "Дхаништха",
    "Шатабхиша",
    "Пурва Бхадрапада",
    "Утара Бхадрапада",
    "Ревати",
]

NAVAMSHA_SIGN_TABLE = (
    (1, 2, 3, 4, 5, 6, 7, 8, 9),
    (10, 11, 12, 1, 2, 3, 4, 5, 6),
    (7, 8, 9, 10, 11, 12, 1, 2, 3),
    (4, 5, 6, 7, 8, 9, 10, 11, 12),
    (1, 2, 3, 4, 5, 6, 7, 8, 9),
    (10, 11, 12, 1, 2, 3, 4, 5, 6),
    (7, 8, 9, 10, 11, 12, 1, 2, 3),
    (4, 5, 6, 7, 8, 9, 10, 11, 12),
    (1, 2, 3, 4, 5, 6, 7, 8, 9),
    (10, 11, 12, 1, 2, 3, 4, 5, 6),
    (7, 8, 9, 10, 11, 12, 1, 2, 3),
    (4, 5, 6, 7, 8, 9, 10, 11, 12),
)

NAVAMSHA_SEGMENT_ARCMINUTES = Decimal("200")


def navamsha_sign_index(sign_index: int, degree_in_sign: float) -> int:
    total_arcminutes = Decimal(str(degree_in_sign)) * Decimal("60")
    segment = int(total_arcminutes // NAVAMSHA_SEGMENT_ARCMINUTES)
    segment = min(segment, 8)
    return NAVAMSHA_SIGN_TABLE[sign_index][segment] - 1


PLANET_LABELS_BG = {
    "Ascendant": "Ас",
    "Sun": "\u0421\u043b",
    "Moon": "Лу",
    "Mercury": "Ме",
    "Venus": "Ве",
    "Mars": "Ма",
    "Jupiter": "Юп",
    "Saturn": "Са",
    "Rahu": "Ра",
    "Ketu": "Ке",
}

PLANET_NAMES_BG = {
    "Ascendant": "Асцендент",
    "Sun": "Слънце",
    "Moon": "Луна",
    "Mercury": "Меркурий",
    "Venus": "Венера",
    "Mars": "Марс",
    "Jupiter": "Юпитер",
    "Saturn": "Сатурн",
    "Rahu": "Раху",
    "Ketu": "Кету",
}

PLANET_ORDER = [
    "Ascendant",
    "Sun",
    "Moon",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Rahu",
    "Ketu",
]

DASHA_SEQUENCE = [
    "Ketu",
    "Venus",
    "Sun",
    "Moon",
    "Mars",
    "Rahu",
    "Jupiter",
    "Saturn",
    "Mercury",
]

DASHA_YEARS = {
    "Ketu": Decimal("7"),
    "Venus": Decimal("20"),
    "Sun": Decimal("6"),
    "Moon": Decimal("10"),
    "Mars": Decimal("7"),
    "Rahu": Decimal("18"),
    "Jupiter": Decimal("16"),
    "Saturn": Decimal("19"),
    "Mercury": Decimal("17"),
}

DASHA_NAMES_BG = {
    "Ketu": "Кету",
    "Venus": "Венера",
    "Sun": "Слънце",
    "Moon": "Луна",
    "Mars": "Марс",
    "Rahu": "Раху",
    "Jupiter": "Юпитер",
    "Saturn": "Сатурн",
    "Mercury": "Меркурий",
}

NODE_MODE_LABELS = {
    "mean": "Среден възел",
    "true": "Истинен възел",
}

_CITY_DATA_PATH = Path(__file__).with_name("cities_bg.json")

CITIES = sorted(
    json.loads(_CITY_DATA_PATH.read_text(encoding="utf-8")),
    key=lambda city: city["name"],
)

CITY_LOOKUP = {city["name"]: city for city in CITIES}
