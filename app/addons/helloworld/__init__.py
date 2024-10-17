from flask import Blueprint

bp = Blueprint("helloworld", __name__)

from app.addons.helloworld import routes