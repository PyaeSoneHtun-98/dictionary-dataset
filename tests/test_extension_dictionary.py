"""Regression coverage for extension validation and packaged lookup ownership."""
from __future__ import annotations

import base64
import contextlib
import io
import json
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_extension_batch as validator
import build_extension_artifact as packager


class ExtensionValidationTests(unittest.TestCase):
    def validate(self, change=None, base="old\nwater\nbottle\n", allow="", rejected="", earlier=False):
        # Alphabetic synthetic keys exercise schema/ownership, not vocabulary.
        entries = [{"word": "test" + chr(97 + i // 26) + chr(97 + i % 26),
                    "pronunciation": "/tɛst/", "forms": [],
                    "meanings": [{"partOfSpeech": "noun", "burmese": ["စမ်းသပ်ချက်"]}]}
                   for i in range(500)]
        number = 62 if earlier else 61
        doc = {"version": 1, "batch": number, "entries": entries}
        if change:
            change(doc)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = root / f"dictionary_batch_{number:03d}.json"
            path.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
            if earlier:
                previous = {"version": 1, "batch": 61, "entries": [
                    {"word": "prior" + e["word"], "forms": ["former" + e["word"]]}
                    for e in entries
                ]}
                previous["entries"][0] = {"word": "previoushead", "forms": ["previousform"]}
                (root / "dictionary_batch_061.json").write_text(json.dumps(previous), encoding="utf-8")
            lookup = root / "base.b64"
            lookup.write_text(base64.b64encode(zlib.compress(base.encode())).decode(), encoding="ascii")
            approved = root / "approved.txt"
            approved.write_text(allow, encoding="utf-8")
            denied = root / "denied.txt"
            denied.write_text(rejected, encoding="utf-8")
            argv = ["validator", str(path), "--base-lookup", str(lookup), "--batches-dir", str(root),
                    "--closed-compound-allowlist", str(approved), "--rejected-headwords", str(denied)]
            output = io.StringIO()
            with patch.object(sys, "argv", argv), contextlib.redirect_stdout(output):
                result = validator.main()
            return result, output.getvalue()

    def test_valid_batch(self):
        self.assertEqual(self.validate()[0], 0)

    def test_rejected_word_cannot_be_allowlisted(self):
        change = lambda d: d["entries"][0].update(word="waterbottle")
        code, output = self.validate(change, allow="waterbottle\n", rejected="waterbottle\n")
        self.assertEqual(code, 1)
        self.assertIn("editorially rejected", output)

    def test_rejected_surface_form(self):
        code, output = self.validate(lambda d: d["entries"][0].update(forms=["waterbottles"]), rejected="waterbottles\n")
        self.assertEqual(code, 1)
        self.assertIn("editorially rejected lookup form", output)

    def test_unreviewed_glued_compound(self):
        code, output = self.validate(lambda d: d["entries"][0].update(word="waterbottle"))
        self.assertEqual(code, 1)
        self.assertIn("suspicious glued", output)

    def test_noncanonical_headwords_and_forms(self):
        for field, value in [("word", "Word"), ("word", "abc1"), ("word", "abc\u200b"),
                             ("forms", ["Forms"]), ("forms", [" spaced "]), ("forms", ["a-b"])]:
            with self.subTest(field=field, value=value):
                self.assertEqual(self.validate(lambda d: d["entries"][0].update({field: value}))[0], 1)

    def test_ipa_rejects_whitespace_invisibles_and_nonipa(self):
        for value in [" /tɛst/", "/tɛst/ ", "/ tɛst/", "/tɛ st/", "/tɛ\u200bst/", "/123/", "/tɛst/other/"]:
            with self.subTest(value=value):
                self.assertEqual(self.validate(lambda d: d["entries"][0].update(pronunciation=value))[0], 1)

    def test_gloss_quality_structure(self):
        for glosses in [["123"], ["English"], ["စမ်းသပ်ချက်", "စမ်းသပ်ချက်"], ["စမ်း\u200bသပ်ချက်"],
                        [" စမ်းသပ်ချက်"], ["စမ်း", "သပ်", "ချက်", "ပို"]]:
            with self.subTest(glosses=glosses):
                self.assertEqual(self.validate(lambda d: d["entries"][0]["meanings"][0].update(burmese=glosses))[0], 1)

    def test_collision_ownership(self):
        def same_batch(d):
            d["entries"][0]["forms"] = [d["entries"][1]["word"]]
        def duplicate_form(d):
            d["entries"][0]["forms"] = ["commonform"]
            d["entries"][1]["forms"] = ["commonform"]
        for change in [same_batch, duplicate_form, lambda d: d["entries"][0].update(forms=["old"]),
                       lambda d: d["entries"][0].update(word="old")]:
            self.assertEqual(self.validate(change)[0], 1)

    def test_schema_and_malformed_pos(self):
        for change in [lambda d: d.update(version=True), lambda d: d.update(unexpected=True),
                       lambda d: d["entries"][0].update(example="extra"),
                       lambda d: d["entries"][0]["meanings"][0].update(partOfSpeech=[]),
                       lambda d: d["entries"][0]["meanings"][0].update(extra=True)]:
            self.assertEqual(self.validate(change)[0], 1)

    def test_prior_extension_ownership_reconstructed_without_current_index(self):
        for key in ["previoushead", "previousform"]:
            for field, value in [("word", key), ("forms", [key])]:
                with self.subTest(key=key, field=field):
                    self.assertEqual(self.validate(lambda d: d["entries"][0].update({field: value}), earlier=True)[0], 1)


class ExtensionArtifactTests(unittest.TestCase):
    def test_packaged_extension_matches_sources_and_all_lookup_owners(self):
        artifact = json.loads((ROOT / packager.ARTIFACT).read_text(encoding="utf-8"))
        rows = [e for p in sorted((ROOT / "DictionaryExtensionBatches").glob("*.json"))
                for e in json.loads(p.read_text(encoding="utf-8"))["entries"]]
        self.assertEqual(artifact, {"version": 1, "entries": sorted(rows, key=lambda e: e["word"])})
        base = validator.load_base_keys(ROOT / "lookup/used_keys_current.zlib.b64")
        owners = {}
        for entry in artifact["entries"]:
            for key in [entry["word"], *entry["forms"]]:
                self.assertNotIn(key, base)
                self.assertNotIn(key, owners)
                owners[key] = entry["word"]
        combined = validator.load_base_keys(ROOT / "extension_lookup/used_keys_current.zlib.b64")
        self.assertEqual(base | owners.keys(), combined)
        metadata = json.loads((ROOT / packager.METADATA).read_text(encoding="utf-8"))
        self.assertEqual(metadata["lookupKeys"], len(owners))

    def test_artifact_determinism_and_digest(self):
        artifact, metadata = packager.build(ROOT)
        self.assertEqual((ROOT / packager.ARTIFACT).read_bytes(), artifact)
        self.assertEqual((ROOT / packager.METADATA).read_bytes(), metadata)


if __name__ == "__main__":
    unittest.main()
