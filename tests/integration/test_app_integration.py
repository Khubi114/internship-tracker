
import os

import pytest
from sqlalchemy import text

from app import Application, create_app, db


@pytest.fixture
def app():
    database_url = os.environ["TEST_DATABASE_URL"]

    if not database_url.endswith("/tracker_test"):
        raise RuntimeError("Use the dedicated tracker_test database only")

    flask_app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": database_url,
    })

    with flask_app.app_context():
        db.drop_all()
        db.create_all()

        yield flask_app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_database_connection(app):
    with app.app_context():
        result = db.session.execute(text("SELECT 1")).scalar()
        assert result == 1


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["database"] == "connected"


def test_create_application(client, app):
    response = client.post("/add", data={
        "company": "Google",
        "position": "Software Intern",
        "application_date": "2026-10-15",
        "status": "Applied",
    })

    assert response.status_code == 302

    with app.app_context():
        record = Application.query.filter_by(company="Google").first()
        assert record is not None
        assert record.position == "Software Intern"


def test_update_application_status(client, app):
    with app.app_context():
        record = Application(
            company="Microsoft",
            position="Data Intern",
            application_date="2026-10-15",
            status="Applied",
        )
        db.session.add(record)
        db.session.commit()
        application_id = record.id

    response = client.post(
        f"/status/{application_id}",
        data={"status": "Interview"},
    )

    assert response.status_code == 302

    with app.app_context():
        updated = db.session.get(Application, application_id)
        assert updated.status == "Interview"


def test_delete_application(client, app):
    with app.app_context():
        record = Application(
            company="Amazon",
            position="Cloud Intern",
            application_date="2026-10-15",
            status="Applied",
        )
        db.session.add(record)
        db.session.commit()
        application_id = record.id

    response = client.post(f"/delete/{application_id}")

    assert response.status_code == 302

    with app.app_context():
        assert db.session.get(Application, application_id) is None
