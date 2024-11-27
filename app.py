# flask app.py
from flask import Flask
from connectors.auth import auth as auth_blueprint

app = Flask(__name__)

app.register_blueprint(auth_blueprint, url_prefix='/auth')

@app.route('/')
def index():
    return '<div>hello </div>'

if __name__ == '__main__':
    app.run(debug=True)
    