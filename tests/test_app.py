import copy

from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Preserve original activities and restore after each test
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


client = TestClient(app)


def test_get_activities():
    # Arrange/Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_prevent_duplicate():
    # Arrange
    activity = "Science Club"
    email = "testuser@example.com"

    # Act: sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # Act: try to sign up again
    resp2 = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert duplicate prevented
    assert resp2.status_code == 400


def test_unregister_participant():
    # Arrange
    activity = "Science Club"
    email = "to_remove@example.com"
    activities[activity]["participants"].append(email)

    # Act
    resp = client.delete(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_nonexistent_participant():
    # Arrange
    activity = "Science Club"
    email = "notfound@example.com"
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Act
    resp = client.delete(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert resp.status_code == 404


def test_activity_not_found_cases():
    # Act / Assert for signup
    resp = client.post("/activities/NoSuchActivity/signup?email=a@b.com")
    assert resp.status_code == 404

    # Act / Assert for delete
    resp2 = client.delete("/activities/NoSuchActivity/signup?email=a@b.com")
    assert resp2.status_code == 404
