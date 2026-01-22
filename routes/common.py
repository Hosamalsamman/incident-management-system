from sqlalchemy.exc import IntegrityError, DataError, SQLAlchemyError
from flask import jsonify, request
from models import db



def commit_trial(success_response):
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
        response = {"success": success_response}
        return jsonify(response), 200