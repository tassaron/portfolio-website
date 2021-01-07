from flask import Blueprint, render_template, flash, current_app
import os
from forms import ContactForm
import requests
import tempfile
import re
from typing import Tuple, Union


try:
    EMAIL_API_KEY = os.environ["EMAIL_API_KEY"]
    EMAIL_API_URL = os.environ["EMAIL_API_URL"]
    EMAIL_SENDER_NAME = os.environ["EMAIL_SENDER_NAME"]
    EMAIL_SENDER_ADDRESS = os.environ["EMAIL_SENDER_ADDRESS"]
    EMAIL_RECEIVER_ADDRESS = os.environ["EMAIL_RECEIVER_ADDRESS"]
except KeyError:
    raise KeyError("You need to create a valid .env file")


contact_blueprint = Blueprint("contact", __name__)


@contact_blueprint.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        try:
            queue_email(
                current_app,
                form.mail_subject.data,
                form.mail_body.data,
                form.sent_by.data,
            )
            flash("Email sent! Thanks", "success")
        except:
            flash("There was an error sending the email", "warning")
            current_app.logger.critical("Error on the contact page!", exc_info=True)
    return render_template("contact.html", form=form)


def queue_email(app, subj, body, respond_to) -> Tuple[bool, Union[str, int]]:
    """
    Queues an email to be sent. First port of entry for ANY email.
    If email is suspected to be spam, write it to a temp file.
    Spam files will be deleted upon termination of the app.

    If succeeded, returns tuple (True, position_in_queue: int)

    If failed, returns tuple (False, path_to_tempfile: str)
    """

    def write_email(out, subj, body, respond_to):
        """Write email somewhere instead of sending it"""
        out(f"/* SUBJECT: {subj}")
        out(str(body))
        out(f"REPLY-TO: {respond_to}")
        out("*/ end of email")

    emails_in_body = re.findall(
        r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", body
    )
    if emails_in_body or " SEO " in body:
        # genuine human beings know that email has its own form field
        # assume only desperate spammers are going to include it twice
        fd, path = tempfile.mkstemp(dir=app.config["SPAM_DIR"], text=True)
        with open(fd, "w") as f:
            write_email(lambda msg: f.write(f"{msg}\n"), subj, body, respond_to)
        return False, path

    app.email_queue.put((subj, body, respond_to))
    app.logger.warning(f"Queuing a new email with subject {subj}")
    n = app.email_queue.qsize()
    if n > 1:
        app.logger.warning(f"The email queue has {n} messages in it")
        app.logger.warning(f"Newly queued email is below:")
        write_email(app.logger.warning, subj, body, respond_to)
    return True, n


def send_email(app, subject, body, respond_to):
    if os.environ["FLASK_ENV"] != "production":
        app.logger.info(
            f"Email would be sent in production: {subject}: {body} from {respond_to}"
        )
        return
    try:
        resp = requests.post(
            f"{EMAIL_API_URL}/messages",
            auth=("api", EMAIL_API_KEY),
            data={
                "from": f"{EMAIL_SENDER_NAME} <{EMAIL_SENDER_ADDRESS}>",
                "to": [f"{EMAIL_RECEIVER_ADDRESS}"],
                "subject": subject,
                "text": f"{body}\n\nRESPOND TO: {respond_to}",
            },
        )
        if resp.status_code != 200:
            app.logger.warning(f"The server responded with {str(resp.status_code)}")
            return False
    except Exception as e:
        app.logger.warning(f"Exception while sending email: {repr(e)}")
        return False
    return True
