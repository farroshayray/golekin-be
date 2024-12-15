from flask import Blueprint

promotion = Blueprint("promotion", __name__)

from . import promotion_routes  
