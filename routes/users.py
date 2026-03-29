import hashlib

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import OperationalError
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User, SectorManagement, Group, AuthorityLevel
from models.users_and_authentication import UserToken
from routes.common import commit_trial, private_route_for_auth_level

users_bp = Blueprint("users_authentication", __name__)


@users_bp.route("/all-active-users")
def active_users():
    users = User.query.filter(User.is_active == True).all()
    users_list = [user.to_dict() for user in users]
    return jsonify(users_list)


@users_bp.route("/register", methods=["GET", "POST"])
def register():
    sectors = SectorManagement.query.all()
    sectors_list = [sector.to_dict() for sector in sectors]
    groups = Group.query.all()
    groups_list = [group.to_dict() for group in groups]
    auth_levels = AuthorityLevel.query.all()
    a_l_list = [a_l.to_dict() for a_l in auth_levels]
    if request.method == "POST":
        data = request.get_json()
        # print(data)
        user = db.session.query(User).filter(User.username == data['username']).first()
        if user:
            return jsonify({"error": "يوجد حساب بهذا الإسم"}), 401
        demanded_sector = SectorManagement.query.get(data['sector_management_id'])
        if data["authority_level_id"] > demanded_sector.authority_level_id:
            return jsonify({"error": f"لا يمكن تسجيل موظف بمستوى صلاحية أعلى من {demanded_sector.authority_level_id} لهذه الإدارة"}), 400
        elif data["authority_level_id"] == demanded_sector.authority_level_id:
            existing_manager = User.query.filter_by(
                sector_management_id=demanded_sector.id,
                authority_level_id=demanded_sector.authority_level_id,
                is_active=True
            ).first()

            if existing_manager:
                return jsonify({"error": "يوجد مدير حالي لهذه الإدارة"}), 400
        hash_and_salted_password = generate_password_hash(
            data['password'],
            method='pbkdf2:sha256',
            salt_length=16
        )
        new_user = User(
            emp_code=data['emp_code'],
            emp_name=data['emp_name'],
            username=data['username'].strip().lower(),
            userpassword=hash_and_salted_password,
            is_active=True,
            sector_management_id=data['sector_management_id'],
            group_id=data['group_id'],
            authority_level_id=data['authority_level_id']
        )

        db.session.add(new_user)
        return commit_trial("تم تسجيل الموظف بنجاح")

    return jsonify(sectors=sectors_list, groups=groups_list, auth_levels=a_l_list)


@users_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        data = request.get_json()
        user = db.session.query(User).filter(User.username == data['username']).first()
        if not user or not check_password_hash(user.userpassword, data['password']):
            return jsonify({"error": "اسم مستخدم أو كلمة مرور خاطئة"}), 401
        else:
            if user.is_active:
                # login token
                token = create_access_token(identity=user.user_id)

                hash_token = hashlib.sha256(data["device_token"].encode()).hexdigest()
                existing_token = UserToken.query.filter_by(token=hash_token).first()
                if not existing_token:
                    new_device_token = UserToken(
                        user_id=user.user_id,
                        token=hash_token
                    )
                    db.session.add(new_device_token)
                    commit_trial("تم الحفظ")
                return jsonify(current_user=user.to_dict(), token=token), 200
            else:
                return jsonify({
                    "error": "هذا الحساب غير مفعل، برجاء مراجعة الادارة العامة لتكنولوجيا المعلومات لتفعيل حسابك"}), 410

    return jsonify({"response": "لا إله إلا الله"})


@users_bp.route("/change-password", methods=["GET", "POST"])
@private_route_for_auth_level(0)
def change_password(current_user):
    if request.method == "POST":
        data = request.get_json()
        if check_password_hash(current_user.userpassword, data['old_password']):
            current_user.userpassword = generate_password_hash(data['new_password'], method='pbkdf2:sha256',
                                                               salt_length=16)
            commit_trial("تم تغيير كلمة المرور بنجاح")
        else:
            return jsonify({"response": "كلمة السر الحالية خاطئة"}), 401
    return jsonify({"response": "سبحان الله وبحمده، سبحان الله العظيم"})


@users_bp.route("/logout", methods=["GET", "POST"])
@private_route_for_auth_level(0)
def logout(current_user):
    if request.method == "POST":
        data = request.get_json()
        hash_token = hashlib.sha256(data["device_token"].encode()).hexdigest()
        existing_token = UserToken.query.filter_by(token=hash_token).first()
        if existing_token:
            db.session.delete(existing_token)
            commit_trial("تم الحذف")
        return jsonify({"response": "تم تسجيل الخروج بنجاح"}), 200
    return jsonify({"response": "لا حول ولا قوة إلا بالله"})