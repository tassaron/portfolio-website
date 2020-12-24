import main
from flask import url_for


app = main.create_app()
app.config["TESTING"] = True
client = app.test_client()


def test_all_basic_routes():
    with app.test_request_context():
        urls = [
            url_for(rule.endpoint)
            for rule in app.url_map.iter_rules()
            if len(rule.arguments) == 0
        ]
    for url in urls:
        resp = client.get(url)
        assert resp.status_code == 200


def test_projects():
    with app.test_request_context():
        for project in ("jezzball", "tabletop", "pyaudiovis", "breakout", "funtimes"):
            resp = client.get(url_for("main.projects", project=project))
            assert resp.status_code == 302


if __name__ == "__main__":
    test_all_basic_routes()
    test_projects()
