from flask import Blueprint

home = Blueprint('home', __name__)

from app.home import views
from app.home import errors
