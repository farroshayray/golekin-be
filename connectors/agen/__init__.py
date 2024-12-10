from flask import Blueprint

agen = Blueprint("agen", __name__)

from . import agen_routes