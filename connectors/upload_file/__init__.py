from flask import Blueprint

upload_file = Blueprint("upload_file", __name__)

from . import upload_route