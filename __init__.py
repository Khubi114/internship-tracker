"""Student Internship Application Tracker (Flask).

PLACEHOLDER from Khubi so the pipeline has something to lint, test and
package. Person D replaces this with the real application. Keep the
create_app() factory and the /health route: the Dockerfile starts
"app:create_app()" and the deploy jobs poll /health.
"""
from flask import Flask, jsonify


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/health")
    def health():
        return jsonify(status="ok"), 200

    return app
