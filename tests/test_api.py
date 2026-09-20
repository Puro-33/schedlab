import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest

from schedlab.server import create_server


class APITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.server = create_server(0, Path(cls.temp.name) / "runs.sqlite3")
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.temp.cleanup()

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port)
        connection.request(method, path, json.dumps(body) if body is not None else None,
                           headers or {"Content-Type": "application/json"})
        response = connection.getresponse()
        data = response.read()
        connection.close()
        return response.status, data

    def test_compare_generate_benchmark(self):
        code, data = self.request("POST", "/api/generate", {"seed": 123, "count": 5})
        self.assertEqual(code, 200)
        code, data = self.request("POST", "/api/compare", json.loads(data))
        self.assertEqual(code, 200)
        self.assertEqual(len(json.loads(data)["results"]), 6)
        code, data = self.request("POST", "/api/benchmark", {"count": 5, "repeats": 2})
        self.assertEqual(code, 200)
        self.assertEqual(len(json.loads(data)["samples"]), 12)

    def test_save_and_reload(self):
        body = {"name": "Research run", "processes": [{"id": "P1", "arrival": 0, "burst": 3}], "quantum": 2}
        code, data = self.request("POST", "/api/experiments", body)
        self.assertEqual(code, 201)
        eid = json.loads(data)["id"]
        code, data = self.request("GET", f"/api/experiments/{eid}")
        self.assertEqual(code, 200)
        payload = json.loads(data)["payload"]
        self.assertEqual(payload["processes"], body["processes"])
        self.assertEqual(payload["quantum"], 2)
        self.assertEqual(len(payload["results"]), 6)
        code, data = self.request("GET", "/api/experiments")
        self.assertIn(eid, [row["id"] for row in json.loads(data)])

    def test_invalid_requests(self):
        for body in ({"processes": []}, [], {"processes": [{"id": "P1", "burst": 1, "arrival": True}]}):
            self.assertEqual(self.request("POST", "/api/compare", body)[0], 400)
        self.assertEqual(self.request("GET", "/api/experiments/missing")[0], 404)
        self.assertEqual(self.request("GET", "/../schedlab/server.py")[0], 404)
        self.assertEqual(self.request("POST", "/api/compare", {}, {"Content-Type": "text/plain"})[0], 415)

    def test_origin_and_host_restrictions(self):
        self.assertEqual(self.request("POST", "/api/generate", {}, {"Content-Type": "application/json", "Origin": "https://example.com"})[0], 403)
        self.assertEqual(self.request("GET", "/api/health", headers={"Host": "example.com"})[0], 403)

    def test_assets_and_health(self):
        for path in ("/", "/app.js", "/style.css", "/api/health"):
            code, body = self.request("GET", path)
            self.assertEqual(code, 200)
            self.assertTrue(body)


if __name__ == "__main__":
    unittest.main()
