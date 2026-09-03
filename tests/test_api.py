"""API tests against the FastAPI application with isolated source data and database."""

from __future__ import annotations

import json
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
    assert [user["id"] for user in response.json()] == [
        "ali",
        "hossein",
        "parsa",
        "reza",
        "shahrad",
    ]


@pytest.mark.parametrize("user_id", ["hossein", "ali", "reza", "parsa", "shahrad"])
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


def test_activity_write_normalizes_whitespace_in_titles(client):
    created = client.post(
        "/api/activities",
        json={
            "userId": "hossein",
            "date": "2026-09-03",
            "title": "  Refactor sync flow  ",
            "status": "planned",
            "projectId": None,
        },
    )
    assert created.status_code == 201
    assert created.json()["title"] == "Refactor sync flow"

    tracked = json.loads(
        (source_files.DATA_ROOT / "activities" / "hossein" / "2026-09-03.json").read_text()
    )
    titles = [activity["title"] for activity in tracked["activities"]]
    assert "Refactor sync flow" in titles


def test_activity_write_rejects_whitespace_only_title(client):
    response = client.post(
        "/api/activities",
        json={
            "userId": "hossein",
            "date": "2026-09-04",
            "title": "   ",
            "status": "planned",
            "projectId": None,
        },
    )
    assert response.status_code == 422
    assert not (source_files.DATA_ROOT / "activities" / "hossein" / "2026-09-04.json").exists()


def test_get_projects_returns_project_collection(client):
    response = client.get("/api/projects")
    assert response.status_code == 200
    projects = response.json()
    assert {project["id"] for project in projects} >= {"team-foundation"}
    assert all(isinstance(project["technology"], list) for project in projects)


def test_create_project_writes_tracked_source_and_appears_in_api(client):
    created = client.post(
        "/api/projects",
        json={
            "userId": "hossein",
            "name": "Calendar Sync",
            "description": "Keep calendar entries synchronized across the team.",
            "technology": ["Python", " React "],
            "status": "planned",
        },
    )
    assert created.status_code == 201
    assert created.json() == {
        "id": "calendar-sync",
        "userId": "hossein",
        "name": "Calendar Sync",
        "description": "Keep calendar entries synchronized across the team.",
        "technology": ["Python", "React"],
        "status": "planned",
    }

    projects = client.get("/api/projects").json()
    assert any(project["id"] == "calendar-sync" for project in projects)

    path = source_files.DATA_ROOT / "projects" / "calendar-sync.json"
    assert path.exists()
    assert any(project.id == "calendar-sync" for project in source_files.load_projects())


def test_create_project_deduplicates_generated_ids(client):
    for expected_id in ("sample-project", "sample-project-2"):
        response = client.post(
            "/api/projects",
            json={
                "userId": "hossein",
                "name": "Sample Project",
                "description": "A duplicate-name project.",
                "technology": [],
                "status": "planned",
            },
        )
        assert response.status_code == 201
        assert response.json()["id"] == expected_id


def test_create_project_rejects_unknown_owner(client):
    response = client.post(
        "/api/projects",
        json={
            "userId": "nobody",
            "name": "Orphan Project",
            "description": "No such owner.",
            "technology": [],
            "status": "planned",
        },
    )
    assert response.status_code == 404
    assert response.json()["error"] == "Not Found"
    assert not (source_files.DATA_ROOT / "projects" / "orphan-project.json").exists()


def test_create_project_rejects_invalid_payloads(client):
    bad_status = client.post(
        "/api/projects",
        json={
            "userId": "hossein",
            "name": "Bad Status",
            "description": "Invalid status value.",
            "technology": [],
            "status": "launched",
        },
    )
    assert bad_status.status_code == 422

    empty_name = client.post(
        "/api/projects",
        json={
            "userId": "hossein",
            "name": "",
            "description": "Empty name.",
            "technology": [],
            "status": "planned",
        },
    )
    assert empty_name.status_code == 422

    invalid_user = client.post(
        "/api/projects",
        json={
            "userId": "Bad User!",
            "name": "Invalid Owner",
            "description": "Owner id is not a slug.",
            "technology": [],
            "status": "planned",
        },
    )
    assert invalid_user.status_code == 422
    assert not (source_files.DATA_ROOT / "projects" / "bad-status.json").exists()


def test_create_project_normalizes_whitespace_in_text_fields(client):
    created = client.post(
        "/api/projects",
        json={
            "userId": "hossein",
            "name": "  Calendar Sync  ",
            "description": "  Keep calendar entries synchronized.  ",
            "technology": [],
            "status": "planned",
        },
    )
    assert created.status_code == 201
    assert created.json()["id"] == "calendar-sync"
    assert created.json()["name"] == "Calendar Sync"
    assert created.json()["description"] == "Keep calendar entries synchronized."

    tracked = {project.id: project for project in source_files.load_projects()}
    assert tracked["calendar-sync"].name == "Calendar Sync"
    assert tracked["calendar-sync"].description == "Keep calendar entries synchronized."


def test_create_project_rejects_whitespace_only_name_and_description(client):
    blank_name = client.post(
        "/api/projects",
        json={
            "userId": "hossein",
            "name": "   ",
            "description": "Name is blank.",
            "technology": [],
            "status": "planned",
        },
    )
    assert blank_name.status_code == 422

    blank_description = client.post(
        "/api/projects",
        json={
            "userId": "hossein",
            "name": "Blank Description",
            "description": "   ",
            "technology": [],
            "status": "planned",
        },
    )
    assert blank_description.status_code == 422

    assert not (source_files.DATA_ROOT / "projects" / "project.json").exists()
    assert not (source_files.DATA_ROOT / "projects" / "blank-description.json").exists()


def test_update_project_rejects_whitespace_only_fields(client):
    created = client.post(
        "/api/projects",
        json={
            "userId": "hossein",
            "name": "Status Board",
            "description": "Original description.",
            "technology": [],
            "status": "planned",
        },
    )
    assert created.status_code == 201
    project_id = created.json()["id"]

    response = client.put(
        f"/api/projects/{project_id}",
        json={
            "userId": "hossein",
            "name": "   ",
            "description": "Name is blank.",
            "technology": [],
            "status": "planned",
        },
    )
    assert response.status_code == 422

    tracked = {project.id: project for project in source_files.load_projects()}
    assert tracked[project_id].name == "Status Board"
    assert tracked[project_id].description == "Original description."
    assert tracked[project_id].status == "planned"


def test_update_project_updates_tracked_source_and_api(client):
    created = client.post(
        "/api/projects",
        json={
            "userId": "hossein",
            "name": "Status Board",
            "description": "Original description.",
            "technology": [],
            "status": "planned",
        },
    )
    assert created.status_code == 201
    project_id = created.json()["id"]

    updated = client.put(
        f"/api/projects/{project_id}",
        json={
            "userId": "hossein",
            "name": "Status Board",
            "description": "Updated description.",
            "technology": ["TypeScript"],
            "status": "active",
        },
    )
    assert updated.status_code == 200
    assert updated.json()["id"] == project_id
    assert updated.json()["description"] == "Updated description."
    assert updated.json()["technology"] == ["TypeScript"]
    assert updated.json()["status"] == "active"

    projects = client.get("/api/projects").json()
    match = [project for project in projects if project["id"] == project_id]
    assert len(match) == 1
    assert match[0]["status"] == "active"
    assert any(project.id == project_id for project in source_files.load_projects())


def test_update_project_supports_owner_change(client):
    created = client.post(
        "/api/projects",
        json={
            "userId": "ali",
            "name": "Handover Project",
            "description": "Owned by ali at first.",
            "technology": [],
            "status": "planned",
        },
    )
    assert created.status_code == 201
    project_id = created.json()["id"]

    updated = client.put(
        f"/api/projects/{project_id}",
        json={
            "userId": "parsa",
            "name": "Handover Project",
            "description": "Now owned by parsa.",
            "technology": [],
            "status": "active",
        },
    )
    assert updated.status_code == 200
    assert updated.json()["userId"] == "parsa"
    tracked = {project.id: project for project in source_files.load_projects()}
    assert tracked[project_id].owner_id == "parsa"


def test_update_unknown_project_returns_structured_404(client):
    response = client.put(
        "/api/projects/does-not-exist",
        json={
            "userId": "hossein",
            "name": "Ghost",
            "description": "No such project.",
            "technology": [],
            "status": "planned",
        },
    )
    assert response.status_code == 404
    assert response.json()["error"] == "Not Found"


def test_update_project_rejects_unknown_owner(client):
    created = client.post(
        "/api/projects",
        json={
            "userId": "hossein",
            "name": "Owner Check",
            "description": "Original owner is valid.",
            "technology": [],
            "status": "planned",
        },
    )
    assert created.status_code == 201
    project_id = created.json()["id"]

    response = client.put(
        f"/api/projects/{project_id}",
        json={
            "userId": "nobody",
            "name": "Owner Check",
            "description": "Invalid new owner.",
            "technology": [],
            "status": "planned",
        },
    )
    assert response.status_code == 404
    tracked = {project.id: project for project in source_files.load_projects()}
    assert tracked[project_id].owner_id == "hossein"
