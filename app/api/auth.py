from flask import jsonify, request, current_app
from flask.views import MethodView
from werkzeug.security import check_password_hash, generate_password_hash

from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError

from app.api.models import session, User
from app.api.utils import token


class UserRegisterAPI(MethodView):
    def post(self):
        username = request.get_json()["username"]
        password = request.get_json()["password"]

        if not username:
            return jsonify({"error": "Username is required."}), 400
        elif not password:
            return jsonify({"error": "Password is required."}), 400

        try:
            stmt = insert(User).values(
                username=username, password=generate_password_hash(password)
            )

            session.execute(stmt)
            session.commit()

            return jsonify({"message": f"User {username} created!"}), 201
        except IntegrityError:
            return jsonify({"error": f"User {username} is already registered."}), 400


class UserLoginAPI(MethodView):
    def post(self):
        results = request.get_json()

        if results.get("username", None):
            stmt = select(User).where(User.username == results["username"])
            user = session.execute(stmt).scalar_one_or_none()

            if user is not None:
                if check_password_hash(user.password, results["password"]):
                    access_token = token.encode(
                        user.id,
                        current_app.config["SECRET_KEY"],
                        expiration_seconds=60 * 60 * 24,
                    )

                    # user.auth_token = access_token

                    # db.session.add(user)
                    # db.session.commit()

                    return (
                        jsonify(
                            {
                                "access_token": access_token,
                                "message": "User logged-in successfully.",
                            }
                        ),
                        200,
                    )
                else:
                    return jsonify({"message": "Wrong email or password"}), 403

        return jsonify({"message": "Wrong email or password"}), 403
