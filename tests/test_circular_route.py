import unittest

from transit import (
    CircularRoute,
    DuplicateStopError,
    EmptyRouteError,
    InvalidStopError,
    StopNotFoundError,
)


def names(stops):
    return [stop.name for stop in stops]


class CircularRouteTest(unittest.TestCase):
    def setUp(self):
        self.route = CircularRoute("Prueba")

    def fill(self, *stop_names):
        for name in stop_names:
            self.route.insert_at_end(name, 5)

    def test_new_route_is_empty(self):
        self.assertTrue(self.route.is_empty())
        self.assertEqual(len(self.route), 0)
        self.assertEqual(self.route.traverse_ahead(), [])
        self.assertTrue(self.route.is_consistent())

    def test_single_stop_points_to_itself(self):
        stop = self.route.insert_at_end("Terminal", 5)
        self.assertIs(stop.stop_ahead, stop)
        self.assertIs(stop.stop_behind, stop)
        self.assertIs(self.route.terminal, stop)

    def test_insert_at_end_keeps_order(self):
        self.fill("A", "B", "C")
        self.assertEqual(names(self.route.traverse_ahead()), ["A", "B", "C"])
        self.assertIs(self.route.terminal.stop_behind.stop_ahead, self.route.terminal)
        self.assertTrue(self.route.is_consistent())

    def test_insert_at_start_changes_terminal(self):
        self.fill("B", "C")
        self.route.insert_at_start("A", 3)
        self.assertEqual(self.route.terminal.name, "A")
        self.assertEqual(names(self.route.traverse_ahead()), ["A", "B", "C"])
        self.assertTrue(self.route.is_consistent())

    def test_insert_at_start_on_empty_route(self):
        stop = self.route.insert_at_start("A", 3)
        self.assertIs(self.route.terminal, stop)
        self.assertTrue(stop.is_isolated())

    def test_insert_after_places_stop_in_the_middle(self):
        self.fill("A", "C")
        self.route.insert_after("A", "B", 4)
        self.assertEqual(names(self.route.traverse_ahead()), ["A", "B", "C"])
        self.assertTrue(self.route.is_consistent())

    def test_insert_after_last_stop_closes_circle(self):
        self.fill("A", "B")
        self.route.insert_after("B", "C", 4)
        self.assertIs(self.route.find("C").stop_ahead, self.route.terminal)

    def test_insert_after_missing_reference_fails(self):
        self.fill("A")
        with self.assertRaises(StopNotFoundError):
            self.route.insert_after("Z", "B", 4)

    def test_traverse_behind_goes_backwards(self):
        self.fill("A", "B", "C", "D")
        self.assertEqual(names(self.route.traverse_behind()), ["A", "D", "C", "B"])

    def test_traverse_from_any_stop(self):
        self.fill("A", "B", "C")
        start = self.route.find("B")
        self.assertEqual(names(self.route.traverse_ahead(start)), ["B", "C", "A"])
        self.assertEqual(names(self.route.traverse_behind(start)), ["B", "A", "C"])

    def test_find_is_case_insensitive(self):
        self.fill("Parque Central")
        self.assertEqual(self.route.find("  parque central ").name, "Parque Central")

    def test_find_missing_stop_fails(self):
        self.fill("A")
        with self.assertRaises(StopNotFoundError):
            self.route.find("Z")

    def test_find_on_empty_route_fails(self):
        with self.assertRaises(EmptyRouteError):
            self.route.find("A")

    def test_remove_middle_stop_relinks_neighbors(self):
        self.fill("A", "B", "C")
        removed = self.route.remove("B")
        self.assertEqual(names(self.route.traverse_ahead()), ["A", "C"])
        self.assertIs(self.route.find("A").stop_ahead, self.route.find("C"))
        self.assertTrue(removed.is_isolated())
        self.assertTrue(self.route.is_consistent())

    def test_remove_terminal_moves_terminal_ahead(self):
        self.fill("A", "B", "C")
        self.route.remove("A")
        self.assertEqual(self.route.terminal.name, "B")
        self.assertEqual(names(self.route.traverse_ahead()), ["B", "C"])
        self.assertTrue(self.route.is_consistent())

    def test_remove_until_one_stop_points_to_itself(self):
        self.fill("A", "B")
        self.route.remove("A")
        self.assertTrue(self.route.terminal.is_isolated())

    def test_remove_last_stop_empties_route(self):
        self.fill("A")
        self.route.remove("A")
        self.assertTrue(self.route.is_empty())
        self.assertEqual(len(self.route), 0)

    def test_no_link_is_none_while_route_has_stops(self):
        self.fill("A", "B", "C")
        self.route.insert_at_start("Z", 2)
        self.route.remove("B")
        for stop in self.route.traverse_ahead():
            self.assertIsNotNone(stop.stop_ahead)
            self.assertIsNotNone(stop.stop_behind)

    def test_total_minutes(self):
        self.route.insert_at_end("A", 5)
        self.route.insert_at_end("B", 7)
        self.assertEqual(self.route.total_minutes(), 12)

    def test_rejects_duplicate_names(self):
        self.fill("A")
        with self.assertRaises(DuplicateStopError):
            self.route.insert_at_end("a", 3)

    def test_rejects_invalid_data(self):
        for name, minutes in [("", 5), ("   ", 5), ("A", "x"), ("A", 0), ("A", -3), ("A", 500), ("A" * 40, 5)]:
            with self.assertRaises(InvalidStopError):
                self.route.insert_at_end(name, minutes)
        self.assertTrue(self.route.is_empty())


if __name__ == "__main__":
    unittest.main()
