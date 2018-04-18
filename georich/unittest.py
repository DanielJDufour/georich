import json
import unittest

from .api.scripts.enrich import run as enrich

class TestEnricher(unittest.TestCase):

    def test_in_memory(self):
        data = [
            {
                "enwiki_title": "sup",
                "pop": 12345678
            },
            {
                "enwiki_title": None,
                "pop": 0
            }
        ]

        expected = [
            {
                "has_enwiki_title": 1,
                "pop": 12345678,
                "has_pop_over_100": 1,
                "has_pop_over_1_000": 1,
                "has_pop_over_1_000_000": 1,
                "pop_is_zero": 0
            }, {
                "has_enwiki_title": 0,
                "has_pop_over_100": 0,
                "has_pop_over_1_000": 0,
                "has_pop_over_1_000_000": 0,
                "pop_is_zero": 1
            }
        ]
        new_fields = [
            "has_enwiki_title",
            "has_pop_over_100",
            "has_pop_over_1_000",
            "has_pop_over_1_000_000",
            "pop_is_zero"
        ]
        actual = enrich(data, new_fields=new_fields, in_memory=True, debug=True)
        print("actual:", actual)
        for index, obj in enumerate(expected):
            for key, value in obj.items():
                try:
                    self.assertEqual(value, actual[index][key])
                except Exception as e:
                    print(key, ":", actual[index][key], "!=", value)
                    raise e
