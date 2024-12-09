from flask import Flask, jsonify, request
from flask_cors import CORS
from config import Config
from models import db
from connectors.auth import auth as auth_blueprint
from connectors.product import products as product_blueprint
from connectors.transaction import transactions as transaction_blueprint
from connectors.upload_file import upload_file as upload_blueprint
from connectors.user import user as user_blueprint
from connectors.cart import cart as cart_blueprint  
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required, unset_jwt_cookies
import os

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
db.init_app(app)
jwt = JWTManager(app)

with app.app_context():
    db.create_all()

# Register blueprint
app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(product_blueprint, url_prefix='/products')
app.register_blueprint(transaction_blueprint, url_prefix='/transaction')  
app.register_blueprint(upload_blueprint, url_prefix='/upload')
app.register_blueprint(user_blueprint, url_prefix='/user')
app.register_blueprint(cart_blueprint, url_prefix='/cart')  

# JWT handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    response = jsonify({"msg": "Token has expired"})
    unset_jwt_cookies(response)
    return response, 401

@jwt.unauthorized_loader
def missing_jwt_callback(error):
    return jsonify({"msg": "Unauthorized, please login first"}), 401

@app.route('/')
def index():
    return '<div>Hello</div>'

if __name__ == '__main__':
    app.run(debug=app.config.get("DEBUG", False))
