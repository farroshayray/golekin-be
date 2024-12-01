from flask import Flask
from config import DevelopmentConfig, ProductionConfig
from models.users import db, User
from connectors.auth import auth as auth_blueprint
import os

app = Flask(__name__)

env = os.getenv("FLASK_ENV", "development")
if env == "development":
    app.config.from_object(DevelopmentConfig)
else:
    app.config.from_object(ProductionConfig)

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
