"""Student Internship Application Tracker."""

import os
import time

from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()

STATUSES = ["Applied", "Interview", "Offer", "Rejected"]


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(120), nullable=False)
    position = db.Column(db.String(120), nullable=False)
    application_date = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="Applied")
    interview_date = db.Column(db.String(20), nullable=True)
    notes = db.Column(db.Text, nullable=True)


def create_app(test_config=None) -> Flask:
    app = Flask(__name__)

    database_url = os.getenv("DATABASE_URL", "sqlite:///local.db")

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.before_request
    def start_request_timer():
        request._start_time = time.perf_counter()

    @app.after_request
    def log_request_time(response):
        start_time = getattr(request, "_start_time", None)

        if start_time is not None:
            duration_ms = (time.perf_counter() - start_time) * 1000

            app.logger.info(
                "request_time_ms=%.2f method=%s path=%s status=%s",
                duration_ms,
                request.method,
                request.path,
                response.status_code,
            )

        return response

    @app.route("/")
    def index():
        applications = Application.query.order_by(Application.id.desc()).all()

        counts = {
            "Applied": Application.query.filter_by(status="Applied").count(),
            "Interview": Application.query.filter_by(status="Interview").count(),
            "Offer": Application.query.filter_by(status="Offer").count(),
            "Rejected": Application.query.filter_by(status="Rejected").count(),
        }

        return render_template(
            "index.html",
            applications=applications,
            statuses=STATUSES,
            counts=counts,
            total=len(applications),
        )

    @app.route("/add", methods=["POST"])
    def add_application():
        company = request.form.get("company", "").strip()
        position = request.form.get("position", "").strip()
        application_date = request.form.get("application_date", "").strip()
        status = request.form.get("status", "Applied").strip()
        interview_date = request.form.get("interview_date", "").strip()
        notes = request.form.get("notes", "").strip()

        if not company or not position or not application_date:
            return redirect(url_for("index"))

        if status not in STATUSES:
            status = "Applied"

        application = Application(
            company=company,
            position=position,
            application_date=application_date,
            status=status,
            interview_date=interview_date or None,
            notes=notes or None,
        )

        db.session.add(application)
        db.session.commit()

        return redirect(url_for("index"))

    @app.route("/edit/<int:application_id>", methods=["GET", "POST"])
    def edit_application(application_id):
        application = db.session.get(Application, application_id)

        if application is None:
            return "Application not found", 404

        if request.method == "POST":
            company = request.form.get("company", "").strip()
            position = request.form.get("position", "").strip()
            application_date = request.form.get(
                "application_date",
                "",
            ).strip()

            if company:
                application.company = company

            if position:
                application.position = position

            if application_date:
                application.application_date = application_date

            status = request.form.get("status", "Applied").strip()

            if status in STATUSES:
                application.status = status

            application.interview_date = (
                request.form.get("interview_date", "").strip() or None
            )

            application.notes = (
                request.form.get("notes", "").strip() or None
            )

            db.session.commit()

            return redirect(url_for("index"))

        return render_template(
            "edit.html",
            application=application,
            statuses=STATUSES,
        )

    @app.route("/status/<int:application_id>", methods=["POST"])
    def update_status(application_id):
        application = db.session.get(Application, application_id)

        if application is None:
            return "Application not found", 404

        status = request.form.get("status", "").strip()

        if status in STATUSES:
            application.status = status
            db.session.commit()

        return redirect(url_for("index"))

    @app.route("/delete/<int:application_id>", methods=["POST"])
    def delete_application(application_id):
        application = db.session.get(Application, application_id)

        if application is None:
            return "Application not found", 404

        db.session.delete(application)
        db.session.commit()

        return redirect(url_for("index"))

    @app.route("/health")
    def health():
        try:
            db.session.execute(text("SELECT 1"))

            return jsonify(
                status="healthy",
                application="running",
                database="connected",
            ), 200

        except Exception:
            db.session.rollback()

            return jsonify(
                status="unhealthy",
                application="running",
                database="disconnected",
            ), 503

    return app