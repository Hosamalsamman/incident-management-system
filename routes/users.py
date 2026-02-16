from flask import Blueprint, jsonify

from models import User

users_bp = Blueprint("users_authentication", __name__)


users_bp.route("/all-active-users")
def active_users():
    users = User.query.filter(User.is_active == True).all()
    users_list = [user.to_dict() for user in users]
    return jsonify(users_list)