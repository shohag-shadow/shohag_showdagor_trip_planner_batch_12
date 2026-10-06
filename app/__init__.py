from flask import Flask,jsonify
from os import environ
from app.models import db
from pathlib import Path
from app.routes import api
def create_app(test_config=None):
    app=Flask(__name__,instance_relative_config=True)
    db_file = Path(app.instance_path)/environ.get("DATABASE_NAME")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_file}"
    db.init_app(app)
    with app.app_context():
        db.create_all()
    @app.route("/health",methods=["GET"])
    def health():
        return jsonify({"status":"ok"}),200
    app.register_blueprint(api)
    return app