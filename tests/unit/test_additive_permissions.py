from food_kg.extractors.additive_permissions import FOOD_CODE, INS


def test_recognises_regulatory_codes() -> None:
    assert INS.fullmatch("160a(i)")
    assert INS.fullmatch("E914")
    assert FOOD_CODE.fullmatch("01.1.4")
    assert FOOD_CODE.fullmatch("12.5")
