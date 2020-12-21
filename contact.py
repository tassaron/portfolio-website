from flask import Blueprint, render_template, flash, current_app
import os
from forms import ContactForm
import requests


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
    return render_template("contact.html", form=form)


def queue_email(app, subj, body, respond_to):
    app.email_queue.put((subj, body, respond_to))
    app.logger.warning(f"Queuing a new email with subject {subj}")
    n = app.email_queue.qsize()
    if n > 1:
        app.logger.warning(f"The email queue has {n} messages in it")
        app.logger.warning(f"Newly queued email is below:")
        app.logger.warning(f"/* SUBJECT: {subj}")
        app.logger.warning(str(body))
        app.logger.warning(f"REPLY-TO: {respond_to}")
        app.logger.warning("*/ end of email")


def send_email(app, subject, body, respond_to):
    if os.environ["FLASK_ENV"] != "production":
        app.logger.info(
            f"Email would be sent in production: {subject}: {body} from {respond_to}"
        )
        return
    requests.post(
        f"{EMAIL_API_URL}/messages",
        auth=("api", EMAIL_API_KEY),
        data={
            "from": f"{EMAIL_SENDER_NAME} <{EMAIL_SENDER_ADDRESS}>",
            "to": [f"{EMAIL_RECEIVER_ADDRESS}"],
            "subject": subject,
            "text": f"{body}\n\nRESPOND TO: {respond_to}",
        },
    )
