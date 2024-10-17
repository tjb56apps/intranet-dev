from flask import Blueprint

bp = Blueprint("powerad", __name__)

from app.addons.powerad import routes