from ingest.classify import classify
from ingest.element import Element


def test_table():
    element = Element(type="table", text="", page=1, bbox=[0, 0, 0, 0], section_path="")
    assert classify(element) == "table"


def test_figure():
    element = Element(type="figure", text="", page=1, bbox=[0, 0, 0, 0], section_path="")
    assert classify(element) == "figure"


def test_safety_warning():
    element = Element(type="text", text="WARNING", page=1, bbox=[0, 0, 0, 0], section_path="")
    assert classify(element) == "safety"


def test_prose():
    element = Element(type="text", text="random text", page=1, bbox=[0, 0, 0, 0], section_path="")
    assert classify(element) == "prose"
