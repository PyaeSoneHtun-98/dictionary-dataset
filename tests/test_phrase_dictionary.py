#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_phrase_batch as validator


def entry(phrase="give up", phrase_type="phrasal_verb", forms=None, burmese=None):
    return {
        "phrase": phrase,
        "type": phrase_type,
        "forms": [] if forms is None else forms,
        "burmese": ["လက်လျှော့သည်"] if burmese is None else burmese,
    }


class PhraseValidationTests(unittest.TestCase):
    def write_batch(self, directory: Path, number: int, entries):
        path = directory / f"phrase_batch_{number:03d}.json"
        path.write_text(
            json.dumps({"version": 1, "batch": number, "entries": entries}, ensure_ascii=False),
            encoding="utf-8",
        )
        return path

    def validate(self, entries, number=1):
        with tempfile.TemporaryDirectory() as td:
            directory = Path(td)
            path = self.write_batch(directory, number, entries)
            with patch.object(validator, "iter_batch_paths", return_value=[]):
                return validator.validate_batch(path, check_manifest=False)

    def valid_250(self):
        return [
            entry(
                phrase=f"test phrase {i}",
                phrase_type="expression",
                burmese=[f"စမ်းသပ် အဓိပ္ပာယ် {i}"],
            )
            for i in range(250)
        ]

    def test_valid_phrase_accepted(self):
        self.assertEqual(self.validate(self.valid_250()), [])

    def test_reject_one_token(self):
        rows = self.valid_250()
        rows[0]["phrase"] = "alone"
        self.assertTrue(self.validate(rows))

    def test_reject_six_tokens(self):
        rows = self.valid_250()
        rows[0]["phrase"] = "one two three four five six"
        self.assertTrue(self.validate(rows))

    def test_reject_unsupported_type(self):
        rows = self.valid_250()
        rows[0]["type"] = "proverb"
        self.assertTrue(self.validate(rows))

    def test_reject_duplicate_canonical(self):
        rows = self.valid_250()
        rows[1]["phrase"] = rows[0]["phrase"]
        self.assertTrue(self.validate(rows))

    def test_reject_canonical_form_collision(self):
        rows = self.valid_250()
        rows[0]["forms"] = ["shared surface"]
        rows[1]["phrase"] = "shared surface"
        self.assertTrue(self.validate(rows))

    def test_reject_form_form_collision(self):
        rows = self.valid_250()
        rows[0]["forms"] = ["same variant"]
        rows[1]["forms"] = ["SAME VARIANT"]
        self.assertTrue(self.validate(rows))

    def test_reject_duplicate_form_same_entry(self):
        rows = self.valid_250()
        rows[0]["forms"] = ["gave up", "GAVE UP"]
        self.assertTrue(self.validate(rows))

    def test_reject_zero_meanings(self):
        rows = self.valid_250()
        rows[0]["burmese"] = []
        self.assertTrue(self.validate(rows))

    def test_reject_more_than_three_meanings(self):
        rows = self.valid_250()
        rows[0]["burmese"] = ["က", "ခ", "ဂ", "ဃ"]
        self.assertTrue(self.validate(rows))

    def test_reject_249_or_251_entries(self):
        rows = self.valid_250()
        self.assertTrue(self.validate(rows[:249]))
        self.assertTrue(self.validate(rows + [entry("extra phrase", "expression")]))

    def test_reject_batch_number_filename_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            directory = Path(td)
            path = directory / "phrase_batch_001.json"
            path.write_text(
                json.dumps({"version": 1, "batch": 2, "entries": self.valid_250()}, ensure_ascii=False),
                encoding="utf-8",
            )
            with patch.object(validator, "iter_batch_paths", return_value=[]):
                self.assertTrue(validator.validate_batch(path, check_manifest=False))


if __name__ == "__main__":
    unittest.main()
