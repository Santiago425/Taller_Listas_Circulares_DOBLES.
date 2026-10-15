import unittest

from transit import BusLine, EmptyRouteError, InvalidStopError, build_sample_line


class BusLineTest(unittest.TestCase):
    def setUp(self):
        self.line = BusLine("Prueba")
        for name, minutes in [("A", 5), ("B", 4), ("C", 6)]:
            self.line.add_stop(name, minutes)

    def test_bus_starts_at_first_stop(self):
        self.assertEqual(self.line.bus_at.name, "A")

    def test_drive_ahead_wraps_around_and_counts_laps(self):
        for _ in range(3):
            self.line.drive_ahead()
        self.assertEqual(self.line.bus_at.name, "A")
        self.assertEqual(self.line.laps, 1)
        self.assertEqual(self.line.elapsed_minutes, 15)

    def test_drive_behind_wraps_around(self):
        self.line.drive_behind()
        self.assertEqual(self.line.bus_at.name, "C")
        self.assertEqual(self.line.elapsed_minutes, 6)

    def test_add_stop_positions(self):
        self.line.add_stop("Z", 2, "start")
        self.line.add_stop("D", 3, "end")
        self.line.add_stop("B2", 3, "after", "B")
        self.assertEqual(self.line.snapshot()["ahead"], ["A", "B", "B2", "C", "D", "Z"])
        self.assertEqual(self.line.snapshot()["terminal"], "Z")

    def test_after_requires_reference(self):
        with self.assertRaises(InvalidStopError):
            self.line.add_stop("D", 3, "after")

    def test_invalid_position(self):
        with self.assertRaises(InvalidStopError):
            self.line.add_stop("D", 3, "middle")

    def test_removing_stop_with_bus_moves_bus_ahead(self):
        self.line.remove_stop("A")
        self.assertEqual(self.line.bus_at.name, "B")

    def test_removing_all_stops_leaves_no_bus(self):
        for name in ["A", "B", "C"]:
            self.line.remove_stop(name)
        self.assertIsNone(self.line.bus_at)
        with self.assertRaises(EmptyRouteError):
            self.line.drive_ahead()

    def test_bus_appears_when_first_stop_is_added(self):
        line = BusLine("Vacía")
        self.assertIsNone(line.bus_at)
        line.add_stop("A", 5)
        self.assertEqual(line.bus_at.name, "A")

    def test_snapshot_traversals_start_at_bus(self):
        self.line.drive_ahead()
        state = self.line.snapshot()
        self.assertEqual(state["ahead"], ["B", "C", "A"])
        self.assertEqual(state["behind"], ["B", "A", "C"])

    def test_sample_line(self):
        line = build_sample_line()
        self.assertEqual(line.route.size, 6)
        self.assertEqual(line.route.total_minutes(), 30)
        self.assertTrue(line.route.is_consistent())


if __name__ == "__main__":
    unittest.main()
