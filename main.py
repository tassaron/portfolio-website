"""
Entrypoint to flask application for tassaron's portfolio website
"""
from dotenv import load_dotenv

load_dotenv()

import os
from flask import Flask, Blueprint, render_template, redirect
from contact import contact_blueprint

main_blueprint = Blueprint("main", __name__)


def create_app():
    if "SECRET_KEY" not in os.environ:
        with open(".env", "a") as f:
            f.write(
                f"\nFLASK_APP=run:app\nFLASK_ENV=development\nSECRET_KEY={os.urandom(24)}\n"
            )
    app = Flask(__name__)
    app.config.update(SECRET_KEY=os.environ.get("SECRET_KEY", os.urandom(24)))
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
