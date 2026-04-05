from functools import wraps
from sqlalchemy.exc import IntegrityError, DataError, SQLAlchemyError
from flask import jsonify, request, g, session as flask_session
from extensions import db
from flask_socketio import SocketIO
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from firebase_admin import messaging
from models import User
from celery import Celery

celery = Celery(
    "ims",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)


def commit_trial(success_response, on_success=None):
    try:
        db.session.commit()
    except IntegrityError as e:
        print(e)
        db.session.rollback()
        return jsonify(
            {"error": "خطأ في تكامل البيانات: قد تكون البيانات مكررة أو غير صالحة"}), 400
    except DataError as e:
        print(e)
        db.session.rollback()
        return jsonify({"error": "خطأ في نوع البيانات أو الحجم"}), 404
    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        return jsonify({"error": "خطأ في قاعدة البيانات"}), 500
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({"error": "حدث خطأ غير متوقع"}), 503
    else:
        if on_success:
            try:
                on_success()  # execute the optional callback
            except Exception as e:
                print(f"Error in on_success callback: {e}")
        response = {"success": success_response}
        return jsonify(response), 200


def private_route_for_groups(allowed_groups):
    def decorator(f):
        # print(f"JWT_SECRET_KEY is set: {os.getenv('FLASK_KEY') is not None}")
        # print(f"JWT_ACCESS_TOKEN_EXPIRES: {app.config.get('JWT_ACCESS_TOKEN_EXPIRES')}")
        @jwt_required()  # Verify JWT token
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get user identity from JWT token
            current_user_id = get_jwt_identity()

            # Load user from database
            user = db.session.get(User, current_user_id)

            if not user:
                return jsonify({'error': 'User not found'}), 403

            # Check if user's group is allowed
            if user.group_id not in allowed_groups:
                return jsonify({'error': 'Access forbidden', 'required_groups': allowed_groups}), 403

            # Pass user to the route function (optional but useful)
            kwargs['current_user'] = user   # pass current_user or **kwargs as input to func to access the object

            # ✅ Store username in g and flask_session for fallback
            g.current_user_username = user.username
            g.current_user_emp_code = user.emp_code
            g.current_user = user
            # flask_session['username'] = user.username

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def private_route_for_auth_level(auth_level):
    def decorator(f):
        # print(f"JWT_SECRET_KEY is set: {os.getenv('FLASK_KEY') is not None}")
        # print(f"JWT_ACCESS_TOKEN_EXPIRES: {app.config.get('JWT_ACCESS_TOKEN_EXPIRES')}")
        @jwt_required()  # Verify JWT token
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get user identity from JWT token
            current_user_id = get_jwt_identity()

            # Load user from database
            user = db.session.get(User, current_user_id)

            if not user:
                return jsonify({'error': 'User not found'}), 403

            # Check if user's group is allowed
            if user.authority_level_id < auth_level:
                return jsonify({'error': 'Access forbidden', 'required_auth_level': auth_level}), 403

            # Pass user to the route function (optional but useful)
            kwargs['current_user'] = user   # pass current_user or **kwargs as input to func to access the object

            # ✅ Store username in g and flask_session for fallback
            g.current_user_username = user.username
            g.current_user_emp_code = user.emp_code
            g.current_user = user
            # flask_session['username'] = user.username

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def add_tokens_to_group(tokens, group_name):
    messaging.subscribe_to_topic(tokens, group_name)


def send_to_group(incident_id, title, body, data=None):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data=data or {},
        topic=f"Team_incident_{incident_id}",
    )

    messaging.send(message)


@celery.task
def send_incident_notification(incident_id, event, body, data=None):
    send_to_group(
        incident_id,
        f"🚨 {event}",
        body,
        data=data or {}
    )