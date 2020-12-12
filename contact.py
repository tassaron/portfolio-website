from flask import Blueprint, render_template, flash
import os
import smtplib
from forms import ContactForm
import logging
import requests


LOG = logging.getLogger(__package__)
if os.environ["FLASK_ENV"] == "development":
    LOG.warning("ATTN: Emails won't send because FLASK_ENV is set to development")

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
    if os.environ["FLASK_ENV"] == "production" and form.validate_on_submit():
        try:
            send_email(form.mail_subject.data, form.mail_body.data, form.sent_by.data)
            flash("Email sent! Thanks", "success")
        except:
            flash("There was an error sending the email", "warning")
    return render_template("contact.html", form=form)


def send_email(subject, body, respond_to):
    return requests.post(
        f"{EMAIL_API_URL}/messages",
        auth=("api", EMAIL_API_KEY),
        data={
            "from": f"{EMAIL_SENDER_NAME} <{EMAIL_SENDER_ADDRESS}>",
            "to": [f"{EMAIL_RECEIVER_ADDRESS}"],
            "subject": subject,
            "text": f"{body}\n\nRESPOND TO: {respond_to}",
        },
    )
