from flask import Flask
from flask_cors import CORS
from config import Config
from models.users import db, User
from connectors.auth import auth as auth_blueprint
import os

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
db.init_app(app)

if env == "development":
    with app.app_context():
        db.create_all()

# Register blueprint
app.register_blueprint(auth_blueprint, url_prefix='/auth')

@app.route('/')
def index():
    return '<div>Hello</div>'

if __name__ == '__main__':
    app.run(debug=app.config.get("DEBUG", False))
