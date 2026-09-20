"""Compare against selected pure functions from the preserved upstream source.

AST extraction deliberately avoids importing the Tkinter application, which
creates windows at module import. The original source is kept unchanged.
"""

import ast
from pathlib import Path
import unittest
from schedlab.engine import simulate


class UpstreamTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parent.parent / "simulator.py"
        tree = ast.parse(path.read_text())
        functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                     and node.name in {"Special", "SJF_NON2", "Respond"}]
        cls.original = {}
        exec(compile(ast.Module(body=functions, type_ignores=[]), str(path), "exec"), cls.original)

    def test_nonpreemptive_sjf_matches_original_example(self):
        rows = [{"id": str(i + 1), "arrival": a, "burst": b}
                for i, (a, b) in enumerate(zip([0, 2, 5, 10, 5], [10, 5, 15, 20, 5]))]
        self.original["SJF_NON2"]([[int(p["id"]), p["arrival"], p["burst"]] for p in rows])
        actual = [[int(s["id"]) if s["id"] else 0, s["start"], s["end"]]
                  for s in simulate(rows, "sjf")["timeline"]]
        self.assertEqual(actual, self.original["ArrayAns"])

    def test_response_metric_corrects_original_absolute_start(self):
        original = self.original["Respond"]([[1, 5, 7]])
        corrected = simulate([{"id": "1", "arrival": 5, "burst": 2}])["metrics"]["mean_response"]
        self.assertEqual(original, 5)
        self.assertEqual(corrected, 0)


if __name__ == "__main__":
    unittest.main()
