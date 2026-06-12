from __future__ import annotations

import os
from datetime import UTC, datetime
from hashlib import sha1
from urllib.parse import urlsplit, urlunsplit


TABLE_NAME = "long_task_resume_smoke"


def _redact_dsn(dsn: str) -> str:
    parsed = urlsplit(dsn)
    host = parsed.hostname or "<host>"
    port = f":{parsed.port}" if parsed.port else ""
    username = parsed.username or "<user>"
    netloc = f"{username}:***@{host}{port}"
    return urlunsplit((parsed.scheme, netloc, parsed.path, "", ""))


def _require_postgres_mode() -> tuple[str, str]:
    mode = os.environ.get("LONG_TASK_RESUME_DEMO_MODE", "fixture").strip().lower()
    dsn = os.environ.get("KSADK_SESSION_DSN", "").strip()
    namespace = os.environ.get("KSADK_SESSION_NAMESPACE", "long_task_resume_demo").strip()

    if mode != "postgres":
        raise SystemExit(
            "pg_smoke.py is opt-in. Set LONG_TASK_RESUME_DEMO_MODE=postgres "
            "and KSADK_SESSION_DSN before running it."
        )
    if not dsn:
        raise SystemExit("KSADK_SESSION_DSN is required in postgres mode.")
    if not namespace:
        raise SystemExit("KSADK_SESSION_NAMESPACE is required in postgres mode.")
    return dsn, namespace


def main() -> int:
    dsn, namespace = _require_postgres_mode()

    try:
        import psycopg
    except ImportError as exc:
        raise SystemExit("Missing dependency: install psycopg[binary] before running pg_smoke.py.") from exc

    run_id = "sample-pg-smoke-" + sha1(f"{namespace}:{datetime.now(UTC).isoformat()}".encode("utf-8")).hexdigest()[:12]
    checkpoint_id = f"{run_id}-cp-1"
    receipt_key = f"{run_id}:deepresearch:report:v1"

    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                    namespace text NOT NULL,
                    run_id text NOT NULL,
                    checkpoint_id text NOT NULL,
                    receipt_key text NOT NULL,
                    status text NOT NULL,
                    created_at timestamptz NOT NULL DEFAULT now(),
                    PRIMARY KEY (namespace, run_id, checkpoint_id, receipt_key)
                )
                """
            )
            cur.execute(
                f"""
                INSERT INTO {TABLE_NAME} (namespace, run_id, checkpoint_id, receipt_key, status)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (namespace, run_id, checkpoint_id, receipt_key)
                DO UPDATE SET status = EXCLUDED.status
                """,
                (namespace, run_id, checkpoint_id, receipt_key, "recorded"),
            )
            cur.execute(
                f"""
                SELECT status
                FROM {TABLE_NAME}
                WHERE namespace = %s AND run_id = %s AND checkpoint_id = %s AND receipt_key = %s
                """,
                (namespace, run_id, checkpoint_id, receipt_key),
            )
            row = cur.fetchone()
            if row != ("recorded",):
                raise SystemExit(f"unexpected smoke row: {row!r}")
            cur.execute(
                f"DELETE FROM {TABLE_NAME} WHERE namespace = %s AND run_id = %s",
                (namespace, run_id),
            )

    print("PG smoke passed")
    print(f"dsn={_redact_dsn(dsn)}")
    print(f"namespace={namespace}")
    print(f"table={TABLE_NAME}")
    print(f"run_id={run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
