import unittest
from dns_kit.bindlite import parse_record, sort_records
from dns_kit.merge_bindlite import *

class Test_merge(unittest.TestCase):
    def setUp(self):
        self.records = ["name type value", 
         "blah blah blah", 
         "something somethingElse AnotherThing"]
        self.conflicts = ["blah blah bleh"]
        self.parsed_records = map(parse_record, self.records)
        self.parsed_conflicts = map(parse_record, self.conflicts)

    def test_parsing(self):
        merged = bind_merge(self.parsed_records)
        self.assertEqual(merged[1], [])
        merged = merged[0]
        self.assertEqual(merged[("name", "type")], "value")
        self.assertEqual(merged[("blah", "blah")], "blah")
        self.assertEqual(merged[("something", "somethingElse")], "AnotherThing")

    def test_conflicts(self):
        merged = bind_merge(self.parsed_records + self.parsed_conflicts)
        self.assertEqual(len(merged[1]), 1)
        self.assertEqual(merged[1][0]["new_value"], "bleh")
        self.assertEqual(merged[1][0]["old_value"], "blah")
        self.assertEqual(merged[1][0]["name"], "blah")
        self.assertEqual(merged[1][0]["type"], "blah")
        merged = merged[0]
        self.assertEqual(merged[("name", "type")], "value")
        self.assertEqual(merged[("blah", "blah")], "bleh")
        self.assertEqual(merged[("something", "somethingElse")], "AnotherThing")

if __name__ == "__main__":
	unittest.main()
