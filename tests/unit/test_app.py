import pytest

from app import Application, create_app, db


@pytest.fixture()
def app():
    test_app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    with test_app.app_context():
        db.create_all()

        yield test_app

        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def test_home_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Student Internship Application Tracker" in response.data


def test_add_application(client, app):
    response = client.post(
        "/add",
        data={
            "company": "Deloitte",
            "position": "Data Analyst Intern",
            "application_date": "2026-10-15",
            "status": "Applied",
            "interview_date": "",
            "notes": "Test application",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        application = Application.query.first()

        assert application is not None
        assert application.company == "Deloitte"
        assert application.position == "Data Analyst Intern"
        assert application.status == "Applied"


def test_edit_application(client, app):
    with app.app_context():
        application = Application(
            company="ANZ",
            position="Intern",
            application_date="2026-10-15",
            status="Applied",
        )

        db.session.add(application)
        db.session.commit()

        application_id = application.id

    response = client.post(
        f"/edit/{application_id}",
        data={
            "company": "ANZ",
            "position": "Data Analyst Intern",
            "application_date": "2026-10-15",
            "status": "Interview",
            "interview_date": "2026-10-20",
            "notes": "Interview booked",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        application = db.session.get(
            Application,
            application_id,
        )

        assert application is not None
        assert application.position == "Data Analyst Intern"
        assert application.status == "Interview"
        assert application.interview_date == "2026-10-20"


def test_update_status(client, app):
    with app.app_context():
        application = Application(
            company="KPMG",
            position="Data Intern",
            application_date="2026-10-15",
            status="Applied",
        )

        db.session.add(application)
        db.session.commit()

        application_id = application.id

    response = client.post(
        f"/status/{application_id}",
        data={
            "status": "Offer",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        application = db.session.get(
            Application,
            application_id,
        )

        assert application is not None
        assert application.status == "Offer"


def test_delete_application(client, app):
    with app.app_context():
        application = Application(
            company="Test Company",
            position="Intern",
            application_date="2026-10-15",
            status="Applied",
        )

        db.session.add(application)
        db.session.commit()

        application_id = application.id

    response = client.post(
        f"/delete/{application_id}",
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        application = db.session.get(
            Application,
            application_id,
        )

        assert application is None