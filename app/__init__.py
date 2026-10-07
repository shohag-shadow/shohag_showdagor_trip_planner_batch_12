from flask import Flask,jsonify
from os import environ
from app.models import db
from pathlib import Path
from app.routes import api
def create_app(test_config=None):
    app=Flask(__name__,instance_relative_config=True)
    app.json.sort_keys = False
    db_file = Path(app.instance_path)/environ.get("DATABASE_NAME")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_file}"
    db.init_app(app)
    with app.app_context():
        db.create_all()
    @app.route("/health",methods=["GET"])
    def health():
        return jsonify({"status":"ok"}),200
    app.register_blueprint(api)
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "INVALID_ROUTE",
            "message": "Route not found, please check for typo or spelling"
        }), 404
        
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "error": "INVALID_METHOD",
            "message": "Method not allowed for this route, please check the HTTP method"
        }), 405

    return app