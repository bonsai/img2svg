from pathlib import Path

from img2svg.router import heuristic_route, load_jev_routes


def test_logo_heuristic():
    route = heuristic_route(Path("my-logo.png"))
    assert route.intent == "logo"
    assert route.mode == "polygon"


def test_jev_jsonl(tmp_path):
    p = tmp_path / "routes.jsonl"
    p.write_text('{"input":"a.png","intent":"diagram","max_colors":8}\n', encoding="utf-8")
    route = load_jev_routes(p)["a.png"]
    assert route.intent == "diagram"
    assert route.max_colors == 8
