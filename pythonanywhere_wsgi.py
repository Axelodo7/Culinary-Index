"""
PythonAnywhere WSGI configuration file.
Upload this as /var/www/axelodo7_pythonanywhere_com_wsgi.py
"""

import sys

# Add your project directory to the sys.path
project_home = '/home/Axelodo7/CulinaryIndex'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
import os
os.environ['SECRET_KEY'] = 'culinary-index-secret'

# Import the Flask app
from app import app as application
