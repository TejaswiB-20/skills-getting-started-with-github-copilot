import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_json():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert data["Chess Club"]["description"].startswith("Learn strategies")


def test_signup_success():
    test_email = "newstudent@mergington.edu"
    url = "/activities/Chess Club/signup?email=" + test_email

    response = client.post(url)

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {test_email} for Chess Club"}
    assert test_email in activities["Chess Club"]["participants"]


def test_duplicate_signup_returns_400():
    duplicate_email = "michael@mergington.edu"
    url = "/activities/Chess Club/signup?email=" + duplicate_email

    response = client.post(url)

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_missing_activity_returns_404():
    response = client.post("/activities/Nonexistent/signup?email=test@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
