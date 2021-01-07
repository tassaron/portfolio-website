"""
Entrypoint to flask application for tassaron's portfolio website
"""
from dotenv import load_dotenv

load_dotenv()

import os
from flask import Flask, Blueprint, render_template, redirect, url_for, abort
from apscheduler.schedulers.background import BackgroundScheduler
from contact import contact_blueprint, send_email
from multiprocessing import Queue
from queue import Empty
from time import time
import tempfile
import shutil
import atexit
import logging
import pytz

try:
    import uwsgi
except ModuleNotFoundError:
    # uwsgi can't be imported when it's not running, such as during a test
    class uWSGI_stub:
        def lock(*_):
            ...

        def unlock(*_):
            ...

        def setprocname(*_):
            ...

    uwsgi = uWSGI_stub()


logging.basicConfig(
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.environ.get("LOG_FILE", "debug.log")),
    ],
    format="%(name)-8.8s [%(levelname)s] %(message)s",
    level=logging.getLevelName(os.environ.get("LOG_LEVEL", "WARNING")),
)


main_blueprint = Blueprint("main", __name__)


def send_scheduled_email(app):
    try:
        email = app.email_queue.get(block=False)
        resp = send_email(app, *email)
        if resp == False:
            app.email_queue.put(email)
    except Empty:
        app.logger.info("No emails to send")


def schedule_emails(app, email_intervals):
    app.email_queue = Queue()
    scheduled_email_queue = BackgroundScheduler(
        daemon=True, timezone=pytz.timezone("America/Toronto")
    )
    for email_interval in email_intervals:
        scheduled_email_queue.add_job(
            lambda: send_scheduled_email(app),
            trigger="cron",
            **email_interval,
        )
    atexit.register(lambda: scheduled_email_queue.shutdown(wait=False))
    scheduled_email_queue.start()


def create_tempdir(prefix):
    """Create named temporary directory which is deleted at exit"""
    directory = tempfile.mkdtemp(prefix=prefix)

    def delete_tempdir():
        shutil.rmtree(directory)

    atexit.register(delete_tempdir)
    return directory


def create_app():
    env_vars = {
        "FLASK_APP": "run:app",
        "FLASK_ENV": "development",
        "SECRET_KEY": os.urandom(24),
    }
    for var, default in env_vars.items():
        if var not in os.environ:
            with open(".env", "a") as f:
                f.write(f"\n{var}={default}")
    load_dotenv()
    app = Flask("portfolio")
    app.config.update(SECRET_KEY=os.environ["SECRET_KEY"])
    app.register_blueprint(main_blueprint)
    app.register_blueprint(contact_blueprint)
    if app.env == "production":
        email_intervals = [
            {
                "hour": "8",
                "minute": "30",
                "second": "10",
            },
            {
                "hour": "13",
                "minute": "37",
                "second": "42",
            },
            {
                "hour": "20",
                "minute": "08",
                "second": "08",
            },
        ]
    else:
        email_intervals = [
            {
                "hour": "*",
                "minute": "*",
                "second": "0",
            },
            {
                "hour": "*",
                "minute": "*",
                "second": "30",
            },
        ]
    uwsgi.lock()
    if os.environ.get("EMAIL_QUEUE") is None:
        pid = str(os.getpid())
        app.logger.info(f"EMAIL_QUEUE is pid {pid}")
        uwsgi.setprocname("uwsgi email queue worker")
        os.environ["EMAIL_QUEUE"] = pid
        schedule_emails(app, email_intervals)
        app.config["SPAM_DIR"] = create_tempdir("SPAM")
    uwsgi.unlock()
    return app


@main_blueprint.route("/")
def index():
    return render_template("index.html")


@main_blueprint.route("/about")
def about():
    return render_template("about.html")


@main_blueprint.route("/projects/<project>")
def projects(project):
    projects = {
        "jezzball": "https://fun.tassaron.com/jezzball",
        "tabletop": "https://dnd.tassaron.com",
        "pyaudiovis": "https://github.com/djfun/audio-visualizer-python/tree/feature-newgui",
        "breakout": "https://fun.tassaron.com/breakout",
        "funtimes": "http://bat.tassaron.com",
    }
    if project in projects:
        return redirect(projects[project])
    abort(404)


@main_blueprint.app_errorhandler(404)
def error(e):
    return render_template("error.html", title=e.name, text=e.description)


if __name__ == "__main__":
    create_app().run(debug=True)
