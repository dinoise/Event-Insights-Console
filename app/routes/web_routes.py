from flask import Blueprint, render_template

bp = Blueprint('web', __name__)

@bp.route('/')
def index_route():
    return render_template('index.html')