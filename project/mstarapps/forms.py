
from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, FloatField, validators
from wtforms.validators import NumberRange
from datetime import timedelta
from flask import session

class SimpleRpmForm(FlaskForm):
    rpm = FloatField("Impeller RPM", validators=[NumberRange(10.0, 60.0, message="value must be in range 10:60")], default=40.0)