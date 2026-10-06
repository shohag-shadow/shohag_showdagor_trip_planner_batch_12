from flask import Flask,jsonify

def create_app(test_config=None):
    app=Flask(__name__,instance_relative_config=True)
    @app.route("/health",methods=["GET"])
    def health():
        return jsonify({"status":"ok"}),200
    return app