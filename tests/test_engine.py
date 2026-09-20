import unittest

from schedlab.engine import ALGORITHMS, compare, simulate
from schedlab.experiments import benchmark, generate


def workload(*items):
    return [{"id": f"P{i + 1}", "arrival": arrival, "burst": burst} for i, (arrival, burst) in enumerate(items)]


class EngineTests(unittest.TestCase):
    def test_hand_computed_fcfs(self):
        result = simulate(workload((0, 8), (1, 4), (2, 2)))
        self.assertEqual([p["completion"] for p in result["processes"]], [8, 12, 14])
        self.assertEqual([p["waiting"] for p in result["processes"]], [0, 7, 10])
        self.assertAlmostEqual(result["metrics"]["mean_turnaround"], 31 / 3)

    def test_shortest_policies(self):
        rows = workload((0, 8), (1, 4), (2, 2))
        self.assertEqual([p["completion"] for p in simulate(rows, "sjf")["processes"]], [8, 14, 10])
        self.assertEqual([p["completion"] for p in simulate(rows, "srtf")["processes"]], [14, 7, 4])

    def test_rr_boundary_arrival_before_requeue(self):
        result = simulate(workload((0, 4), (2, 1)), "rr", 2)
        self.assertEqual([s["id"] for s in result["timeline"]], ["P1", "P2", "P1"])
        self.assertEqual([p["completion"] for p in result["processes"]], [5, 3])

    def test_idle_intervals_and_utilization(self):
        result = simulate(workload((3, 2), (10, 1)), "srtf")
        self.assertEqual(result["timeline"], [
            {"id": None, "start": 0, "end": 3}, {"id": "P1", "start": 3, "end": 5},
            {"id": None, "start": 5, "end": 10}, {"id": "P2", "start": 10, "end": 11}])
        self.assertAlmostEqual(result["metrics"]["utilization"], 3 / 11)

    def test_priority_and_hrrn(self):
        rows = workload((0, 4), (0, 8), (1, 2))
        rows[0]["priority"] = 1
        rows[1]["priority"] = 0
        self.assertEqual(simulate(rows, "priority")["timeline"][0]["id"], "P2")
        self.assertEqual([s["id"] for s in simulate(rows, "hrrn")["timeline"]], ["P1", "P3", "P2"])

    def test_stable_ties(self):
        for algorithm in ALGORITHMS:
            self.assertEqual(simulate(workload((0, 1), (0, 1)), algorithm)["timeline"][0]["id"], "P1")

    def test_invariants_across_seeded_workloads(self):
        for seed in range(30):
            rows = generate(seed, 15)
            for result in compare(rows, (seed % 7) + 1):
                service = {p["id"]: 0 for p in rows}
                last = 0
                for segment in result["timeline"]:
                    self.assertEqual(segment["start"], last)
                    self.assertGreater(segment["end"], last)
                    last = segment["end"]
                    if segment["id"]:
                        service[segment["id"]] += segment["end"] - segment["start"]
                for p in result["processes"]:
                    self.assertEqual(service[p["id"]], p["burst"])
                    self.assertGreaterEqual(p["waiting"], 0)
                    self.assertGreaterEqual(p["response"], 0)
                    self.assertLessEqual(p["response"], p["waiting"])
                    self.assertEqual(p["turnaround"], p["waiting"] + p["burst"])
                self.assertEqual(last, result["metrics"]["makespan"])

    def test_srtf_against_independent_tick_oracle(self):
        for seed in range(25):
            rows = generate(seed, 10)
            remaining = [p["burst"] for p in rows]
            completion = [0] * len(rows)
            time = 0
            while any(remaining):
                eligible = [i for i, p in enumerate(rows) if p["arrival"] <= time and remaining[i]]
                if eligible:
                    i = min(eligible, key=lambda j: (remaining[j], rows[j]["arrival"], j))
                    remaining[i] -= 1
                    if not remaining[i]:
                        completion[i] = time + 1
                time += 1
            self.assertEqual([p["completion"] for p in simulate(rows, "srtf")["processes"]], completion)

    def test_invalid_input(self):
        for rows in ([], None, [{}], workload((0, 0)), workload((-1, 2)), [{"id": "<script>", "arrival": 0, "burst": 1}], workload((False, 2))):
            with self.assertRaises(ValueError):
                simulate(rows)
        with self.assertRaises(ValueError):
            simulate(workload((0, 1)), "rr", 0)
        with self.assertRaises(ValueError):
            simulate(workload((0, 1)), [])

    def test_reproducible_benchmarks(self):
        self.assertEqual(generate(42), generate(42))
        result = benchmark(repeats=3, count=5)
        self.assertEqual(result, benchmark(repeats=3, count=5))
        self.assertEqual(len(result["samples"]), 18)
        self.assertEqual(len(result["summary"]), 6)


if __name__ == "__main__":
    unittest.main()
