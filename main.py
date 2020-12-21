"""
Entrypoint to flask application for tassaron's portfolio website
"""
from dotenv import load_dotenv

load_dotenv()

import os
from flask import Flask, Blueprint, render_template, redirect
from apscheduler.schedulers.background import BackgroundScheduler
from contact import contact_blueprint, send_email
from multiprocessing import Queue
from queue import Empty, Full
from time import time
import atexit
import logging


logging.basicConfig(
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.environ.get("LOG_FILE", "debug.log")),
    ],
    format="%(asctime)s %(name)-8.8s [%(levelname)s] %(message)s",
    level=logging.getLevelName(os.environ.get("LOG_LEVEL", "WARNING")),
)


main_blueprint = Blueprint("main", __name__)


def send_scheduled_email(app):
    try:
        last_run = app.email_cooldown.get(block=False)
    except Empty:
        app.logger.debug("Another process has the cooldown variable right now")
        return
    if time() - last_run < (29 if app.env != "production" else 24 * 60 * 50):
        app.logger.debug("Too soon between emails")
        try:
            app.email_cooldown.put(last_run, block=True, timeout=1)
        except Full:
            app.logger.debug("Cooldown queue was full")
        return

    try:
        email = app.email_queue.get(block=False)
        send_email(app, *email)
        app.email_cooldown.put(time())
    except Empty:
        app.logger.info("No emails to send")
        app.email_cooldown.put(last_run)


def schedule_emails(app, email_interval):
    app.email_queue = Queue()
    app.email_cooldown = Queue(maxsize=1)
    app.email_cooldown.put(time())
    scheduled_email_queue = BackgroundScheduler(daemon=True)
    scheduled_email_queue.add_job(
        lambda: send_scheduled_email(app),
        "cron",
        **email_interval,
    )
    atexit.register(lambda: scheduled_email_queue.shutdown(wait=False))
    scheduled_email_queue.start()


def create_app():
    if "SECRET_KEY" not in os.environ:
        with open(".env", "a") as f:
            f.write(
                f"\nFLASK_APP=run:app\nFLASK_ENV=development\nSECRET_KEY={os.urandom(24)}\n"
            )
    app = Flask(__name__)
    app.config.update(SECRET_KEY=os.environ.get("SECRET_KEY", os.urandom(24)))
    if app.env == "production":
        email_interval = {
            "hour": "8",
            "minute": "30",
            "second": "10",
        }
    else:
        email_interval = {
            "hour": "*",
            "minute": "*",
            "second": "*/30",
        }
    schedule_emails(app, email_interval)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(contact_blueprint)
    return app


@main_blueprint.route("/")
def index():
    return render_template("index.html")


@main_blueprint.route("/about")
def about():
    return render_template("about.html")


@main_blueprint.route("/projects/")
def projectsBaseDir():
    return redirect("https://rainey.tech", code=301)


@main_blueprint.route("/projects/<projectName>")
def projects(projectName):
    if projectName == "jezzball":
        return redirect("https://fun.tassaron.com/jezzball", code=301)
    elif projectName == "dnd":
        return redirect("https://dnd.tassaron.com/", code=301)
    elif projectName == "pyaudiovis":
        return redirect(
            "https://github.com/djfun/audio-visualizer-python/tree/feature-newgui",
            code=301,
        )
    elif projectName == "breakout":
        return redirect("https://fun.tassaron.com/breakout", code=301)
    elif projectName == "funtimes":
        return redirect("http://bat.tassaron.com", code=301)


if __name__ == "__main__":
    create_app().run(debug=True)
