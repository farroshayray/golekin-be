# flask app.py
from flask import Flask
from config import Config
from models.users import db, User
from connectors.auth import auth as auth_blueprint

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(auth_blueprint, url_prefix='/auth')

@app.route('/')
def index():
    return '<div>hello </div>'

if __name__ == '__main__':
    app.run(debug=True)
    