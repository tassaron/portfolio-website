from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
)


class ContactForm(FlaskForm):
    """A Flask-WTF form to send me an email"""

    mail_subject = StringField("Subject: ", validators=[Length(min=5, max=250)])
    mail_body = TextAreaField(validators=[DataRequired(), Length(min=5)])
    sent_by = StringField("Your Email: ", validators=[DataRequired(), Email()])
    submit = SubmitField("Send Email")
