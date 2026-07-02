"""Test-Infrastruktur: eine echte Postgres in Docker.

Ein Container pro Test-Session, ein frisches Schema pro Test.
Setzt ERD2OKF_TEST_DSN, um eine bereits laufende Postgres zu nutzen (CI).
"""

import os
import subprocess
import time
import uuid

import psycopg
import pytest

_IMAGE = "postgres:17-alpine"
_PASSWORD = "erd2okf-test"


def _wait_ready(dsn: str, timeout: float = 60.0) -> None:
    deadline = time.monotonic() + timeout
    while True:
        try:
            with psycopg.connect(dsn, connect_timeout=3):
                return
        except psycopg.OperationalError:
            if time.monotonic() > deadline:
                raise
            time.sleep(0.5)


@pytest.fixture(scope="session")
def pg_dsn():
    """DSN einer laufenden Postgres (extern via ERD2OKF_TEST_DSN oder Docker)."""
    external = os.environ.get("ERD2OKF_TEST_DSN")
    if external:
        _wait_ready(external)
        yield external
        return

    name = f"erd2okf-test-{uuid.uuid4().hex[:8]}"
    subprocess.run(
        [
            "docker", "run", "--rm", "-d", "--name", name,
            "-e", f"POSTGRES_PASSWORD={_PASSWORD}",
            "-p", "127.0.0.1::5432",
            _IMAGE,
        ],
        check=True,
        capture_output=True,
    )
    try:
        port = subprocess.run(
            ["docker", "port", name, "5432/tcp"],
            check=True, capture_output=True, text=True,
        ).stdout.strip().splitlines()[0].rsplit(":", 1)[1]
        dsn = f"postgresql://postgres:{_PASSWORD}@127.0.0.1:{port}/postgres"
        _wait_ready(dsn)
        yield dsn
    finally:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True)


@pytest.fixture
def db(pg_dsn):
    """Verbindung mit frischem, leerem Schema `public`."""
    with psycopg.connect(pg_dsn, autocommit=True) as conn:
        conn.execute("DROP SCHEMA public CASCADE")
        conn.execute("CREATE SCHEMA public")
        yield conn
