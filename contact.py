from flask import Blueprint, render_template, flash
import os
import smtplib
from forms import ContactForm
import logging


LOG = logging.getLogger(__package__)
if os.environ["FLASK_ENV"] == "development":
    LOG.warning("ATTN: Emails won't send because FLASK_ENV is set to development")

try:
    EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
    EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
except KeyError:
    raise KeyError("You need to create a valid .env file")


contact_blueprint = Blueprint("contact", __name__)


@contact_blueprint.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        if os.environ["FLASK_ENV"] == "development":
            flash("Email sent! Thanks", "success")
            return render_template("contact.html", form=form)
        # Production
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            subject = form.mail_subject.data
            body = form.mail_body.data
            msg = f"Subject: {subject}\n\n{body}\RESPOND TO: {form.sent_by.data}"
            try:
                smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg)
                flash("Email sent! Thanks", "success")
            except:
                flash("There was an error sending the email", "warning")
    return render_template("contact.html", form=form)
