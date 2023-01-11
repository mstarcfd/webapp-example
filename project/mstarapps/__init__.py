from flask import Blueprint

app_blueprint = Blueprint("mstarapp", __name__, url_prefix="/mstarapp", template_folder="templates")

from . import models, views, forms  # noqa