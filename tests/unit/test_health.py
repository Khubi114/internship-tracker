from app import create_app, db


def test_health_returns_healthy():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    with app.app_context():
        db.create_all()

        client = app.test_client()

        response = client.get("/health")

        assert response.status_code == 200

        data = response.get_json()

        assert data["status"] == "healthy"
        assert data["application"] == "running"
        assert data["database"] == "connected"