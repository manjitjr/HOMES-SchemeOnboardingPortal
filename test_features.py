#!/usr/bin/env python3
from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


SLOT_MONTHS = [1, 4, 7, 11]


def _auth_headers(client: TestClient, username: str, password: str = "password") -> dict:
    res = client.post("/api/auth/login", json={"username": username, "password": password})
    assert res.status_code == 200, f"login failed for {username}: {res.status_code} {res.text}"
    token = res.json().get("token")
    assert token, f"missing token for {username}"
    return {"Authorization": f"Bearer {token}"}


def _next_slot_year_month() -> tuple[int, int]:
    today = date.today()
    for month in SLOT_MONTHS:
        if month >= today.month:
            return today.year, month
    return today.year + 1, SLOT_MONTHS[0]


def test_auth_seeded_users_can_login():
    with TestClient(app) as client:
        for username in ["moh_creator", "moh_approver", "mto_admin"]:
            res = client.post("/api/auth/login", json={"username": username, "password": "password"})
            assert res.status_code == 200
            body = res.json()
            assert body.get("token")
            assert body.get("user", {}).get("username") == username


def test_scheme_workflow_and_slot_review_flow():
    with TestClient(app) as client:
        creator_h = _auth_headers(client, "moh_creator")
        approver_h = _auth_headers(client, "moh_approver")
        admin_h = _auth_headers(client, "mto_admin")

        unique = uuid4().hex[:8]
        scheme_name = f"Regression Scheme {unique}"
        scheme_code = f"MOH_{unique}"

        create_res = client.post(
            "/api/schemes",
            headers=creator_h,
            json={
                "agency": "MOH",
                "scheme_name": scheme_name,
                "scheme_code": scheme_code,
                "legislated_or_consent": "Legislated",
            },
        )
        assert create_res.status_code == 201, create_res.text
        scheme_id = create_res.json()["id"]

        year, month = _next_slot_year_month()
        tech_date = date(year, month, 1).isoformat()
        biz_date = date(year, month, min(28, 15)).isoformat()

        slot_set_res = client.put(
            f"/api/schemes/{scheme_id}/slot",
            headers=creator_h,
            json={
                "year": year,
                "slot_month": month,
                "technical_go_live": tech_date,
                "business_go_live": biz_date,
            },
        )
        assert slot_set_res.status_code == 200, slot_set_res.text

        submit_res = client.post(f"/api/schemes/{scheme_id}/submit", headers=creator_h)
        assert submit_res.status_code == 200, submit_res.text
        assert submit_res.json().get("status") == "pending_review"

        approve_res = client.post(f"/api/schemes/{scheme_id}/approve", headers=approver_h)
        assert approve_res.status_code == 200, approve_res.text
        assert approve_res.json().get("status") == "pending_final"

        slot_approve_res = client.post(
            f"/api/schemes/{scheme_id}/slot/approve",
            headers=admin_h,
            json={"approval_status": "approved", "approver_comment": "Looks good"},
        )
        assert slot_approve_res.status_code == 200, slot_approve_res.text

        final_res = client.post(f"/api/schemes/{scheme_id}/final-approve", headers=admin_h)
        assert final_res.status_code == 200, final_res.text
        assert final_res.json().get("status") == "approved"

        my_bookings_res = client.get("/api/scheduling/my-bookings", headers=creator_h)
        assert my_bookings_res.status_code == 200, my_bookings_res.text
        bookings = my_bookings_res.json().get("bookings", [])
        assert any(b.get("submission_id") == scheme_id for b in bookings)

        overview_res = client.get(f"/api/scheduling/overview/{year}", headers=admin_h)
        assert overview_res.status_code == 200, overview_res.text
        quarters = overview_res.json().get("quarters", [])
        all_booking_ids = [entry.get("submission_id") for q in quarters for entry in q.get("bookings", [])]
        assert scheme_id in all_booking_ids


def test_mto_admin_can_read_notification_logs_endpoint():
    with TestClient(app) as client:
        admin_h = _auth_headers(client, "mto_admin")
        logs_res = client.get("/api/schemes/notification-logs", headers=admin_h)
        assert logs_res.status_code == 200, logs_res.text
        assert isinstance(logs_res.json(), list)
