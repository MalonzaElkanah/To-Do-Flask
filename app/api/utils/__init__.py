from flask import g, jsonify, request, current_app
from sqlalchemy import select

import functools

from app.api.models import User, session
from app.api.utils.token import decode


def token_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            token = request.headers.get("Authorization")

        if not token:
            return jsonify({"message": "Token is required"}), 401

        try:
            token = token.split("Bearer ")[1]
            data = decode(token, current_app.config["SECRET_KEY"])
            if data.get("data", None):
                stmt = select(User).where(User.id == data.get("data"))
                user = session.execute(stmt).scalar_one_or_none()

                # if user.auth_token is None:
                #    return jsonify({"message": "Token has been expired!"}), 400
                g.user = user
            else:
                return jsonify({"message": data.get("error", "Token is invalid!")}), 400
        except Exception as e:
            print("error", e)
            return jsonify({"message": "Token is invalid."}), 400

        return view(*args, **kwargs)

    return wrapped_view
