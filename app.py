from flask import Flask
from config import Config
from routes import setup_routes

# Initialize the Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Setup the routes
setup_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
