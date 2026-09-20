"""Local web app. Run: python3 -m schedlab.server"""

import argparse
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4

from .engine import ALGORITHMS, compare
from .experiments import benchmark, generate

ROOT = Path(__file__).resolve().parent.parent
ASSETS = {"/": ("index.html", "text/html"), "/app.js": ("app.js", "text/javascript"),
          "/style.css": ("style.css", "text/css")}


@contextmanager
def connect(path):
    db = sqlite3.connect(path, timeout=10)
    db.row_factory = sqlite3.Row
    try:
        with db:
            yield db
    finally:
        db.close()


def create_server(port=8080, database=None):
    database = Path(database) if database else ROOT / "data" / "experiments.sqlite3"
    database.parent.mkdir(parents=True, exist_ok=True)
    with connect(database) as db:
        db.execute("CREATE TABLE IF NOT EXISTS experiments (id TEXT PRIMARY KEY, name TEXT NOT NULL, created TEXT NOT NULL, payload TEXT NOT NULL)")

    class Handler(BaseHTTPRequestHandler):
        def send(self, code, body, mime="application/json"):
            data = json.dumps(body, allow_nan=False).encode() if mime == "application/json" else body
            self.send_response(code)
            self.send_header("Content-Type", mime + "; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(data)

        def allowed(self):
            allowed_hosts = {f"localhost:{self.server.server_port}", f"127.0.0.1:{self.server.server_port}"}
            host = self.headers.get("Host", "")
            origin = self.headers.get("Origin")
            return host in allowed_hosts and (origin is None or origin == f"http://{host}")

        def do_GET(self):
            if not self.allowed():
                return self.send(403, {"error": "Use the local application address"})
            path = urlsplit(self.path).path
            if path in ASSETS:
                filename, mime = ASSETS[path]
                return self.send(200, (ROOT / "web" / filename).read_bytes(), mime)
            if path == "/api/health":
                return self.send(200, {"status": "ok", "algorithms": ALGORITHMS})
            if path == "/api/experiments":
                with connect(database) as db:
                    rows = db.execute("SELECT id, name, created FROM experiments ORDER BY created DESC LIMIT 100").fetchall()
                return self.send(200, [dict(row) for row in rows])
            if path.startswith("/api/experiments/"):
                with connect(database) as db:
                    row = db.execute("SELECT * FROM experiments WHERE id = ?", (path.rsplit("/", 1)[1],)).fetchone()
                if row:
                    return self.send(200, {**dict(row), "payload": json.loads(row["payload"])})
            self.send(404, {"error": "Not found"})

        def do_POST(self):
            if not self.allowed():
                return self.send(403, {"error": "Cross-origin requests are not allowed"})
            try:
                if self.headers.get_content_type() != "application/json":
                    return self.send(415, {"error": "Use application/json"})
                if self.headers.get("Transfer-Encoding"):
                    return self.send(400, {"error": "Transfer encoding is not supported"})
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 65536:
                    return self.send(413, {"error": "Request must contain 1–65536 bytes"})
                self.connection.settimeout(10)
                body = json.loads(self.rfile.read(size))
                if not isinstance(body, dict):
                    raise ValueError("Request body must be an object")
                path = urlsplit(self.path).path
                if path == "/api/generate":
                    return self.send(200, {"processes": generate(body.get("seed", 42), body.get("count", 12), body.get("profile", "mixed"))})
                if path == "/api/compare":
                    return self.send(200, {"results": compare(body.get("processes"), body.get("quantum", 3))})
                if path == "/api/benchmark":
                    return self.send(200, benchmark(**{k: body[k] for k in ("seed", "count", "profile", "repeats", "quantum") if k in body}))
                if path == "/api/experiments":
                    name = body.get("name", "Untitled experiment")
                    if not isinstance(name, str) or not 1 <= len(name.strip()) <= 80:
                        raise ValueError("Name must contain 1–80 characters")
                    rows, quantum = body.get("processes"), body.get("quantum", 3)
                    results = compare(rows, quantum)
                    payload = {"processes": rows, "quantum": quantum, "results": results, "engine_version": "1.0.0"}
                    eid, created = uuid4().hex, datetime.now(timezone.utc).isoformat()
                    with connect(database) as db:
                        db.execute("INSERT INTO experiments VALUES (?, ?, ?, ?)",
                                   (eid, name.strip(), created, json.dumps(payload)))
                    return self.send(201, {"id": eid, "name": name.strip(), "created": created})
                self.send(404, {"error": "Not found"})
            except (ValueError, TypeError, UnicodeError) as error:
                self.send(400, {"error": str(error)})
            except sqlite3.Error:
                self.send(503, {"error": "Experiment storage is temporarily unavailable"})

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main():
    parser = argparse.ArgumentParser(description="SchedLab local research dashboard")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--database", type=Path)
    args = parser.parse_args()
    server = create_server(args.port, args.database)
    print(f"SchedLab running at http://127.0.0.1:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
