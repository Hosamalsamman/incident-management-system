from flask import Blueprint, jsonify, request
from extensions import db
from models import SectorBranch
from models.gis_data import Valve
from routes.common import commit_trial, private_route_for_auth_level

gis_bp = Blueprint("gis_bp", __name__)

@gis_bp.route("/all-valves")
@private_route_for_auth_level(2)
def get_all_valves(current_user):

    valves = (
        Valve.query
        .join(SectorBranch, Valve.branch_id == SectorBranch.branch_id)
        .filter(
            SectorBranch.sector_management_id == current_user.sector_management_id
        )
        .limit(10)
        .all()
    )
    print(len(valves))

    return jsonify([v.to_dict() for v in valves])