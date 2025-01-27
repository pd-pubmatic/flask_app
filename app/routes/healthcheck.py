from flask import jsonify, Blueprint

healthcheck = Blueprint('healthcheck', __name__)

@healthcheck.route("/healthcheck", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200 