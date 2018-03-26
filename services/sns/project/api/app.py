from flask import Blueprint


sns_blueprint = Blueprint('sns', __name__)


@sns_blueprint.route('/')
def hello():
    return 'Hello'
