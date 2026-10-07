import copy
import string
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import phrase_extension_common as common


def entry(phrase="lawyer up", forms=None, burmese=None):
    return {"phrase": phrase, "type": "phrasal_verb",
            "forms": forms or [], "burmese": burmese or ["ရှေ့နေငှားသည်"]}


class PhraseExtensionTests(unittest.TestCase):
    def test_reject_frozen_canonical_and_frozen_form(self):
        owners, _, _ = common.base_dataset()
        for surface in ["give up", "gave up"]:
            self.assertTrue(common.validate_entries([entry(surface)], owners.copy()))

    def test_reject_prior_form_collision(self):
        self.assertTrue(common.validate_entries(
            [entry(forms=["lawyered up"])], {"lawyered up": "earlier:lawyer up"}))

    def test_reject_forward_canonical_form_collision(self):
        rows = [entry(forms=["lawyered up"]), entry("lawyered up")]
        self.assertTrue(common.validate_entries(rows, {}))

    def test_reject_duplicate_meanings(self):
        self.assertTrue(common.validate_entries(
            [entry(burmese=["ရှေ့နေငှားသည်", "ရှေ့နေငှားသည်"])], {}))

    def test_reject_non_burmese_and_mixed_english(self):
        for gloss in ["lawyer", "123", "ရှေ့နေ lawyer"]:
            self.assertTrue(common.validate_entries([entry(burmese=[gloss])], {}))

    def test_reject_invisible_characters(self):
        for value in [entry("lawyer\u200b up"), entry(burmese=["ရှေ့နေ\u200bငှားသည်"])]:
            self.assertTrue(common.validate_entries([value], {}))

    def test_reject_placeholder_or_long_expression(self):
        for surface in ["rat [someone] out", "one two three four five six"]:
            self.assertTrue(common.validate_entries([entry(surface)], {}))

    def test_accept_reviewed_irregular_forms(self):
        row = entry("run out of steam", ["runs out of steam", "ran out of steam", "running out of steam"])
        self.assertEqual(common.validate_entries([row], {}), [])

    def test_accept_plural_possessive_apostrophe(self):
        self.assertEqual(common.validate_entries([entry("at your wits' end")], {}), [])

    def test_reject_own_form_and_uppercase_form(self):
        for forms in [["lawyer up"], ["Lawyered up"]]:
            self.assertTrue(common.validate_entries([entry(forms=forms)], {}))

    def test_batch_size_number_and_integer_version(self):
        rows = [entry(f"test phrase {a}{b}")
                for a in string.ascii_lowercase for b in string.ascii_lowercase][:250]
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "phrase_batch_013.json"
            valid = {"version": 1, "batch": 13, "entries": rows}
            path.write_bytes(common.json_bytes(valid))
            self.assertEqual(len(common.read_batch(path, 13, {})), 250)
            for change in [{"entries": rows[:249]}, {"batch": 14}, {"version": True}]:
                bad = copy.deepcopy(valid)
                bad.update(change)
                path.write_bytes(common.json_bytes(bad))
                with self.assertRaises(ValueError):
                    common.read_batch(path, 13, {})

    def test_reject_batch_gap(self):
        with patch.object(common, "extension_paths", return_value=[Path("phrase_batch_014.json")]):
            with self.assertRaisesRegex(ValueError, "Expected extension batch 013"):
                common.snapshots()

    def test_detect_snapshot_drift(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "snapshot.json"
            with patch.object(common, "ROOT", Path(td)):
                common.write_or_check(path, b"{}\n", True)
                common.write_or_check(path, b"{}\n", False)
                with self.assertRaises(ValueError):
                    common.write_or_check(path, b"{\"changed\": true}\n", False)

    def test_actual_snapshots_are_deterministic_and_current(self):
        first = common.snapshots()
        self.assertEqual(first, common.snapshots())
        manifest, encoded, raw, metadata = first
        for path, contents in [(common.MANIFEST, common.json_bytes(manifest)),
                               (common.INDEX, (encoded + "\n").encode("ascii")),
                               (common.ARTIFACT, raw),
                               (common.METADATA, common.json_bytes(metadata))]:
            common.write_or_check(path, contents, False)
        self.assertEqual(manifest["extensionPhrases"], manifest["extensionBatchCount"] * 250)
        self.assertEqual(manifest["totalPhrases"], 3000 + manifest["extensionPhrases"])


if __name__ == "__main__":
    unittest.main()
