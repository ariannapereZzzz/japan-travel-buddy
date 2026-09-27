import json
from pathlib import Path


def test_japan_2026_fixture_shape() -> None:
    path = Path(__file__).resolve().parents[1] / "app" / "data" / "japan_2026.json"
    data = json.loads(path.read_text())
    assert data["slug"] == "japan-2026"
    assert len(data["route"]) == 5
    assert len(data["days"]) == 15
    assert len(data["legs"]) == 7
    assert len(data["hotels"]) == 3
    assert len(data["packing"]) == 4
    assert len(data["tips"]) == 5
    assert sum(len(day["tasks"]) for day in data["days"]) > 0
