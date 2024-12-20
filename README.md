# Setting Up a Golekin Project Using Flask Project with Poetry

This documentation outlines the steps to set up a Python Flask project using Poetry for dependency management.

## Prerequisites

- Python 3.8 or higher installed on your system
- Poetry installed ([Installation Guide](https://python-poetry.org/docs/#installation))

---

## Steps

### 1. Create a New Project Directory

Create a directory for your Flask project:

```bash
mkdir flask_project
cd flask_project
```

### 2. Initialize a Poetry Project

Run the following command to initialize a new Poetry project:

```bash
poetry init
```

You will be prompted to answer several questions about your project (e.g., name, version, description). Fill these out as needed.

### 3. Install Flask

Use Poetry to add Flask as a dependency:

```bash
poetry add flask
```

This will install Flask and add it to your `pyproject.toml` file.

### 4. Configure the Virtual Environment

Activate the virtual environment managed by Poetry:

```bash
poetry shell
```

### 5. Create the Project Structure

Set up a basic Flask project structure:

```
flask_project/
├── app/
│   ├── __init__.py
│   ├── routes.py
├── tests/
│   ├── __init__.py
│   └── test_routes.py
├── pyproject.toml
└── README.md
```

- **`app/__init__.py`**:
  ```python
  from flask import Flask

  def create_app():
      app = Flask(__name__)

      from .routes import main
      app.register_blueprint(main)

      return app
  ```

- **`app/routes.py`**:
  ```python
  from flask import Blueprint

  main = Blueprint('main', __name__)

  @main.route('/')
  def home():
      return "Hello, Flask with Poetry!"
  ```

### 6. Run the Application

Create a file `run.py` in the project root to start the Flask server:

```python
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
```

Run the application:

```bash
python run.py
```

Visit `http://127.0.0.1:5000` in your browser to verify that the application is running.

### 7. Add Development Dependencies (Optional)

Install additional tools for development, such as `pytest` and `flask-testing`:

```bash
poetry add --dev pytest flask-testing
```

### 8. Run Tests

Set up a basic test in `tests/test_routes.py`:

```python
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home(client):
    response = client.get('/')
    assert response.data == b"Hello, Flask with Poetry!"
```

Run tests using:

```bash
pytest
```

### 9. Lock Dependencies

After adding all dependencies, lock the versions in `poetry.lock`:

```bash
poetry lock
```

### 10. Add a `.env` File (Optional)

Use a `.env` file to manage environment variables. Install `python-dotenv`:

```bash
poetry add python-dotenv
```

Then, load environment variables in `app/__init__.py`:

```python
from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')

    from .routes import main
    app.register_blueprint(main)

    return app
```

### 11. Dockerize the Application (Optional)

Create a `Dockerfile` for containerizing your Flask app:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN pip install poetry && poetry install

COPY . /app

CMD ["poetry", "run", "python", "run.py"]
```

Build and run the Docker container:

```bash
docker build -t flask_poetry_app .
docker run -p 5000:5000 flask_poetry_app
```

---

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

---

