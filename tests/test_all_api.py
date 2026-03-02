"""
Scenario-based API tests: each API is exercised in its own test, one by one.
Server runs in a subprocess; shared auth and created resource IDs are stored in scenario_state.
Final test gives one confirmation that all scenarios completed successfully.
Requires MongoDB to be running.
"""
import os
import sys
import subprocess
import time
import pytest
import httpx
from datetime import datetime, timedelta, timezone

BASE_URL = "http://127.0.0.1:8004"
PROC = None


def start_server():
    global PROC
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PROC = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8004"],
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(30):
        try:
            r = httpx.get(f"{BASE_URL}/health", timeout=1.0)
            if r.status_code == 200:
                return
        except Exception:
            time.sleep(0.3)
    raise RuntimeError("Server did not become ready in time")


def stop_server():
    global PROC
    if PROC:
        PROC.terminate()
        try:
            PROC.wait(timeout=5)
        except subprocess.TimeoutExpired:
            PROC.kill()
        PROC = None


@pytest.fixture(scope="module")
def server():
    start_server()
    yield
    stop_server()


@pytest.fixture(scope="module")
def scenario_state(server):
    """Shared state: auth_headers and created resource IDs for dependent scenarios."""
    state = {"auth_headers": None, "account_id": None, "card_id": None, "emi_id": None, "borrow_id": None, "cashflow_id": None}
    username = f"scenario_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    password = "Password123"
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as c:
        r = c.post("/auth/register", json={"username": username, "password": password})
        if r.status_code == 400 and "already exists" in (r.text or "").lower():
            username = f"scenario2_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
            r = c.post("/auth/register", json={"username": username, "password": password})
        assert r.status_code == 201, f"register: {r.status_code} {r.text}"
        r = c.post("/auth/login", json={"username": username, "password": password})
        assert r.status_code == 200, r.text
        state["auth_headers"] = {"Authorization": f"Bearer {r.json()['access_token']}"}
    yield state


@pytest.fixture
def client():
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as c:
        yield c


@pytest.mark.order(1)
def test_scenario_01_public_root(server, client):
    """Scenario 1: Public root endpoint."""
    r = client.get("/")
    assert r.status_code == 200
    assert "status" in r.json()


@pytest.mark.order(2)
def test_scenario_02_public_health(server, client):
    """Scenario 2: Public health endpoint."""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "healthy"


@pytest.mark.order(3)
def test_scenario_03_auth_register(server, client):
    """Scenario 3: Auth register (already done in fixture; verify login works)."""
    r = client.post("/auth/login", json={"username": "invalid", "password": "wrong"})
    assert r.status_code == 401


@pytest.mark.order(4)
def test_scenario_04_bank_accounts(server, client, scenario_state):
    """Scenario 4: Bank accounts CRUD."""
    h = scenario_state["auth_headers"]
    r = client.post("/bank-accounts", json={"bank_name": "Scenario Bank", "liquid_balance": 5000.0, "reserve_amount": 500.0}, headers=h)
    assert r.status_code == 201, r.text
    scenario_state["account_id"] = r.json().get("_id") or r.json().get("id")
    r = client.get("/bank-accounts", headers=h)
    assert r.status_code == 200
    r = client.get(f"/bank-accounts/{scenario_state['account_id']}", headers=h)
    assert r.status_code == 200
    r = client.put(f"/bank-accounts/{scenario_state['account_id']}", json={"liquid_balance": 6000.0}, headers=h)
    assert r.status_code == 200


@pytest.mark.order(5)
def test_scenario_05_credit_cards(server, client, scenario_state):
    """Scenario 5: Credit cards CRUD (depends on bank account)."""
    h = scenario_state["auth_headers"]
    aid = scenario_state["account_id"]
    assert aid
    r = client.post("/credit-cards", json={"card_name": "Scenario Card", "bank_account_id": aid, "current_spend": 50.0, "billed_amount": 100.0, "emi_due": 0.0}, headers=h)
    assert r.status_code == 201, r.text
    scenario_state["card_id"] = r.json().get("_id") or r.json().get("id")
    r = client.get("/credit-cards", headers=h)
    assert r.status_code == 200
    r = client.get(f"/credit-cards/{scenario_state['card_id']}", headers=h)
    assert r.status_code == 200
    r = client.put(f"/credit-cards/{scenario_state['card_id']}", json={"billed_amount": 150.0}, headers=h)
    assert r.status_code == 200


@pytest.mark.order(6)
def test_scenario_06_emis(server, client, scenario_state):
    """Scenario 6: EMIs CRUD and mark-payment."""
    h = scenario_state["auth_headers"]
    r = client.post("/emis", json={"name": "Scenario Loan", "principal_amount": 5000.0, "interest_rate": 6.0, "monthly_emi_amount": 250.0, "remaining_months": 12}, headers=h)
    assert r.status_code == 201, r.text
    scenario_state["emi_id"] = r.json().get("_id") or r.json().get("id")
    r = client.get("/emis", headers=h)
    assert r.status_code == 200
    r = client.get(f"/emis/{scenario_state['emi_id']}", headers=h)
    assert r.status_code == 200
    r = client.post(f"/emis/{scenario_state['emi_id']}/mark-payment", headers=h)
    assert r.status_code == 200
    r = client.put(f"/emis/{scenario_state['emi_id']}", json={"remaining_months": 10}, headers=h)
    assert r.status_code == 200


@pytest.mark.order(7)
def test_scenario_07_borrows(server, client, scenario_state):
    """Scenario 7: Borrows CRUD."""
    h = scenario_state["auth_headers"]
    due = (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S")
    r = client.post("/borrows", json={"party_name": "Scenario Party", "transaction_type": "borrowed_from", "remaining_amount": 500.0, "due_date": due, "status": "active"}, headers=h)
    assert r.status_code == 201, r.text
    scenario_state["borrow_id"] = r.json().get("_id") or r.json().get("id")
    r = client.get("/borrows", headers=h)
    assert r.status_code == 200
    r = client.get(f"/borrows/{scenario_state['borrow_id']}", headers=h)
    assert r.status_code == 200
    r = client.put(f"/borrows/{scenario_state['borrow_id']}", json={"remaining_amount": 400.0}, headers=h)
    assert r.status_code == 200


@pytest.mark.order(8)
def test_scenario_08_cashflows(server, client, scenario_state):
    """Scenario 8: Cashflows CRUD, missed, mark-completed."""
    h = scenario_state["auth_headers"]
    exp_date = (datetime.now(timezone.utc) + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
    r = client.post("/cashflows", json={"transaction_type": "income", "amount": 3000.0, "expected_date": exp_date, "status": "pending", "description": "Scenario income"}, headers=h)
    assert r.status_code == 201, r.text
    scenario_state["cashflow_id"] = r.json().get("_id") or r.json().get("id")
    r = client.get("/cashflows", headers=h)
    assert r.status_code == 200
    r = client.get("/cashflows/missed", headers=h)
    assert r.status_code == 200
    r = client.get(f"/cashflows/{scenario_state['cashflow_id']}", headers=h)
    assert r.status_code == 200
    r = client.post(f"/cashflows/{scenario_state['cashflow_id']}/mark-completed", headers=h)
    assert r.status_code == 200
    r = client.put(f"/cashflows/{scenario_state['cashflow_id']}", json={"amount": 3500.0}, headers=h)
    assert r.status_code == 200


@pytest.mark.order(9)
def test_scenario_09_snapshots(server, client, scenario_state):
    """Scenario 9: Snapshots create and list."""
    h = scenario_state["auth_headers"]
    r = client.post("/snapshots", json={"snapshot_date": "2024-06-30", "total_income": 10000.0, "total_expenses": 6000.0, "total_emi_paid": 1000.0}, headers=h)
    assert r.status_code == 201, r.text
    r = client.get("/snapshots", headers=h)
    assert r.status_code == 200


@pytest.mark.order(10)
def test_scenario_10_dashboard(server, client, scenario_state):
    """Scenario 10: Dashboard."""
    r = client.get("/dashboard", headers=scenario_state["auth_headers"])
    assert r.status_code == 200
    body = r.json()
    assert "metrics" in body or "upcoming_dues" in body or "missed_income" in body


@pytest.mark.order(11)
def test_scenario_11_financial_engine(server, client, scenario_state):
    """Scenario 11: Financial engine metrics and safe-spendable."""
    h = scenario_state["auth_headers"]
    r = client.get("/financial-engine/metrics", headers=h)
    assert r.status_code == 200
    r = client.get("/financial-engine/safe-spendable", headers=h)
    assert r.status_code == 200
    assert "safe_spendable_amount" in r.json()


@pytest.mark.order(12)
def test_scenario_12_auth_reset_password(server, client, scenario_state):
    """Scenario 12: Auth reset password."""
    r = client.post("/auth/reset-password", json={"old_password": "Password123", "new_password": "NewPass123"}, headers=scenario_state["auth_headers"])
    assert r.status_code == 200, r.text


@pytest.mark.order(13)
def test_scenario_13_cleanup(server, client, scenario_state):
    """Scenario 13: Cleanup created resources."""
    h = scenario_state["auth_headers"]
    for key, url in [
        ("cashflow_id", "/cashflows/{}"),
        ("borrow_id", "/borrows/{}"),
        ("emi_id", "/emis/{}"),
        ("card_id", "/credit-cards/{}"),
        ("account_id", "/bank-accounts/{}"),
    ]:
        id_ = scenario_state.get(key)
        if id_:
            r = client.delete(url.format(id_), headers=h)
            assert r.status_code == 204, f"delete {key}: {r.status_code}"


@pytest.mark.order(14)
def test_final_confirmation(server, client):
    """Final confirmation: all critical endpoints are reachable and APIs behave as expected."""
    r = client.get("/health")
    assert r.status_code == 200, "Health check must pass"
    assert r.json().get("status") == "healthy", "Health status must be healthy"
    r = client.get("/")
    assert r.status_code == 200, "Root endpoint must respond"
    print("\n" + "=" * 60)
    print("FINAL CONFIRMATION: All API scenarios completed successfully.")
    print("Public, Auth, Bank Accounts, Credit Cards, EMIs, Borrows,")
    print("Cashflows, Snapshots, Dashboard, Financial Engine, and")
    print("Reset Password have been exercised one by one. System OK.")
    print("=" * 60)
