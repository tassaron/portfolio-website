import main
from contact import queue_email
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


def test_spam_simple():
    success, _ = queue_email(
        app, "test", "Improve SEO for your site", "test@example.com"
    )
    assert success == False


def test_spam_regex():
    success, _ = queue_email(
        app, "test", "Contact at test@example.com", "test@example.com"
    )
    assert success == False


def test_spam_tempfile():
    testdata = ("test", "Improve SEO for your site", "test@example.com")
    _, path = queue_email(app, *testdata)
    with open(path, "r") as f:
        subj, body, respond_to, _ = f.readlines()
        subj = subj.split(": ", 1)[1].strip()
        body = body.strip()
        respond_to = respond_to.split(": ", 1)[1].strip()
    assert (subj, body, respond_to) == testdata


def test_queue_email_success():
    success, pos = queue_email(
        app, "test", "birdhouse in your soul", "test@example.com"
    )
    assert success == True
    assert pos == 1
    success, pos = queue_email(
        app, "test", "birdhouse in your soul", "test@example.com"
    )
    assert success == True
    assert pos == 2


if __name__ == "__main__":
    test_all_basic_routes()
    test_projects()
