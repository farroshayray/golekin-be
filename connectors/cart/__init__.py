# cart blueprint __init__.py to cart_route.py
from flask import Blueprint

cart = Blueprint("cart", __name__)

from . import cart_routes