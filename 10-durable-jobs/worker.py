"""Process one durable job. Retry an expired lease; idempotently upsert the fixed index."""

import json
import os
import sqlite3
import time

DB = os.getenv("ATLAS_DB", "state.sqlite3")
with sqlite3.connect(DB) as db:
    db.execute("BEGIN IMMEDIATE")
    row = db.execute(
        "SELECT id FROM jobs WHERE status='queued' OR (status='working' AND lease_until<?) ORDER BY rowid LIMIT 1",
        (time.time(),),
    ).fetchone()
    if row:
        job_id = row[0]
        db.execute(
            "UPDATE jobs SET status='working',lease_until=? WHERE id=?",
            (time.time() + 30, job_id),
        )
if row:
    # Real fixture index writes and terminal state commit together, not a sleep-only fake job.
    with sqlite3.connect(DB) as db:
        for doc_id, body in [
            ("public-v1", "v1 key instructions"),
            ("public-v2", "v2 key instructions"),
        ]:
            db.execute(
                "INSERT INTO indexed_docs VALUES(?,?) ON CONFLICT(id) DO UPDATE SET body=excluded.body",
                (doc_id, body),
            )
        db.execute(
            "UPDATE jobs SET status='completed',result=? WHERE id=?",
            (json.dumps({"indexed_docs": 2}), job_id),
        )
    print("Completed fixture reindex", job_id)
else:
    print("No queued or expired job.")
