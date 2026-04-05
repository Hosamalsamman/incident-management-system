from flask import Blueprint, jsonify, request
from extensions import db
from models.gis_data import Valve
from routes.common import commit_trial

gis_bp = Blueprint("gis_bp", __name__)

@gis_bp.route("/all-valves")
def get_all_valves():
    valves = Valve.query.all()
    valves_list = [v.to_dict() for v in valves]
    return jsonify(valves_list)