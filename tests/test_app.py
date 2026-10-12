import pytest

from app import app as flask_app


@pytest.fixture()
def client(tmp_path):
    flask_app.config.update(
        TESTING=True,
        DATABASE=str(tmp_path / "test.db"),
        SECRET_KEY="test-secret",
    )
    with flask_app.test_client() as test_client:
        yield test_client


def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"ACEest Fitness" in response.data


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_register_member(client):
    response = client.post(
        "/members",
        data={"name": "Asha", "email": "asha@example.com"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Asha" in response.data
    assert b"Member registered successfully" in response.data


def test_duplicate_email_is_rejected(client):
    data = {"name": "Asha", "email": "asha@example.com"}
    client.post("/members", data=data)
    response = client.post("/members", data=data, follow_redirects=True)
    assert b"already registered" in response.data


def test_workout_can_be_logged(client):
    client.post("/members", data={"name": "Asha", "email": "asha@example.com"})
    response = client.post(
        "/workouts",
        data={"member_id": "1", "activity": "Yoga", "minutes": "45"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Yoga" in response.data
    assert b"45 minutes" in response.data


def test_invalid_workout_minutes_are_rejected(client):
    client.post("/members", data={"name": "Asha", "email": "asha@example.com"})
    response = client.post(
        "/workouts",
        data={"member_id": "1", "activity": "Yoga", "minutes": "0"},
        follow_redirects=True,
    )
    assert b"minutes must be between 1 and 600" in response.data
