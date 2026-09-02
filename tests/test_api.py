"""API tests against the FastAPI application with isolated source data and database."""

from __future__ import annotations

import shutil

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.database import source_files
from backend.database.connection import REPOSITORY_ROOT
from backend.database.init_db import initialize_database


@pytest.fixture()
def client(tmp_path, monkeypatch):
    data_root = tmp_path / "data"
    shutil.copytree(REPOSITORY_ROOT / "data", data_root)
    monkeypatch.setattr(source_files, "DATA_ROOT", data_root)

    database_path = tmp_path / "test.db"
    initialize_database(database_path, seed=True)
    monkeypatch.setenv("DATABASE_PATH", str(database_path))
    with TestClient(app) as test_client:
        yield test_client


def test_api_health_returns_ok(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_legacy_health_endpoint_still_works(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_get_users_returns_example_team_members(client):
    response = client.get("/api/users")
    assert response.status_code == 200
    assert [user["id"] for user in response.json()] == ["ali", "hossein", "reza"]


@pytest.mark.parametrize("user_id", ["hossein", "ali", "reza"])
def test_get_user_returns_member(client, user_id):
    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id


def test_get_unknown_user_returns_structured_404(client):
    response = client.get("/api/users/does-not-exist")
    assert response.status_code == 404
    assert response.json()["error"] == "Not Found"


def test_get_activities_returns_tracked_activities(client):
    response = client.get("/api/activities")
    assert response.status_code == 200
    activities = response.json()
    assert activities[0]["userId"] == "ali"
    assert all(activity["id"] for activity in activities)


def test_activity_crud_updates_tracked_source_and_api(client):
    created = client.post(
        "/api/activities",
        json={
            "userId": "hossein",
            "date": "2026-09-01",
            "title": "Review pull requests",
            "status": "planned",
            "projectId": "team-foundation",
        },
    )
    assert created.status_code == 201
    activity_id = created.json()["id"]

    updated = client.put(
        f"/api/activities/{activity_id}",
        json={
            "userId": "hossein",
            "date": "2026-09-02",
            "title": "Review and merge pull requests",
            "status": "completed",
            "projectId": "team-foundation",
        },
    )
    assert updated.status_code == 200
    assert updated.json()["id"] == activity_id
    assert updated.json()["date"] == "2026-09-02"
    assert updated.json()["status"] == "completed"

    activities = client.get("/api/activities").json()
    matches = [activity for activity in activities if activity["id"] == activity_id]
    assert len(matches) == 1
    assert matches[0]["title"] == "Review and merge pull requests"

    deleted = client.delete(f"/api/activities/{activity_id}")
    assert deleted.status_code == 204
    assert all(activity["id"] != activity_id for activity in client.get("/api/activities").json())


def test_activity_write_validates_user_and_project(client):
    unknown_user = client.post(
        "/api/activities",
        json={
            "userId": "nobody",
            "date": "2026-09-01",
            "title": "Invalid",
            "status": "planned",
            "projectId": None,
        },
    )
    assert unknown_user.status_code == 404

    unknown_project = client.post(
        "/api/activities",
        json={
            "userId": "hossein",
            "date": "2026-09-01",
            "title": "Invalid project",
            "status": "planned",
            "projectId": "does-not-exist",
        },
    )
    assert unknown_project.status_code == 404


def test_get_projects_returns_project_collection(client):
    response = client.get("/api/projects")
    assert response.status_code == 200
    projects = response.json()
    assert {project["id"] for project in projects} >= {"team-foundation"}
    assert all(isinstance(project["technology"], list) for project in projects)
