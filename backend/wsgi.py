from app import create_app
import os

# Create the 'app' object that Gunicorn will use.
# It's good practice to default to 'production' here,
# as this file is specifically for the Gunicorn server.
app = create_app(os.getenv('FLASK_ENV', 'production'))
