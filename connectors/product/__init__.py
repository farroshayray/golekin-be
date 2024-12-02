from flask import Blueprint

products = Blueprint("products", __name__)

from . import product_routes  
