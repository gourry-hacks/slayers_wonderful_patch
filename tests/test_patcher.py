"""Small end-to-end packages exercise input policy without shipping disc data."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch as mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import patch

spec = importlib.util.spec_from_file_location("build_release", ROOT / "maintainer/build_release.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def metadata(name, data):
    return {"name": name, "size": len(data), "sha256": hashlib.sha256(data).hexdigest()}


class PatcherTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / "original.bin"
        self.source.write_bytes(bytes(range(256)) * 32)
        self.target = self.root / "english.bin"
        self.target_bytes = b"translated" + self.source.read_bytes()[10:]
        self.target.write_bytes(self.target_bytes)
        self.cue_bytes = (
            b'FILE "wonderful_patched.bin" BINARY\r\n'
            b'  TRACK 01 MODE2/2352\r\n'
            b'    INDEX 01 00:00:00\r\n'
        )
        expected = {
            "source": {"bin": metadata("original.bin", self.source.read_bytes())},
            "target": {"bin": metadata("wonderful_patched.bin", self.target_bytes),
                       "cue": metadata("wonderful_patched.cue", self.cue_bytes)},
        }
        # Build a real package with no CUE inputs at all.
        with mock.object(builder, "REPO_ROOT", self.root), mock.object(builder, "EXPECTED", expected), \
             mock.object(sys, "argv", ["build_release.py", "--source-bin", str(self.source), "--target-bin", str(self.target)]), \
             contextlib.redirect_stdout(io.StringIO()):
            builder.main()
        self.output = self.root / "output"

    def run_patcher(self, *args):
        with mock.object(patch, "REPO_ROOT", self.root), \
             mock.object(patch, "MANIFEST_PATH", self.root / "release_manifest.json"), \
             mock.object(sys, "argv", ["patch.py", "--bin", str(self.source), "--output-dir", str(self.output), *args]), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as errors:
            result = patch.main()
        return result, errors.getvalue()

    def test_no_cue_needed_and_outputs_match(self):
        result, errors = self.run_patcher()
        self.assertEqual(result, 0, errors)
        self.assertEqual((self.output / "wonderful_patched.bin").read_bytes(), self.target_bytes)
        self.assertEqual((self.output / "wonderful_patched.cue").read_bytes(), self.cue_bytes)
        manifest = json.loads((self.root / "release_manifest.json").read_text())
        self.assertEqual(set(manifest["source"]), {"bin"})
        self.assertEqual(set(manifest["patches"]), {"bin"})

    def test_optional_cue_content_does_not_affect_output(self):
        cue = self.root / "renamed.cue"
        for content in (b'', b'REM comment\nFILE "other-name.bin" BINARY\n',
                        b'\xef\xbb\xbfFILE "windows.bin" BINARY\r\n'):
            with self.subTest(content=content):
                cue.write_bytes(content)
                result, errors = self.run_patcher("--cue", str(cue), "--force")
                self.assertEqual(result, 0, errors)
                self.assertEqual((self.output / "wonderful_patched.cue").read_bytes(), self.cue_bytes)
                self.assertEqual(cue.read_bytes(), content)

    def test_nonexistent_optional_cue_is_not_opened(self):
        result, errors = self.run_patcher("--cue", str(self.root / "missing.cue"))
        self.assertEqual(result, 0, errors)

    def test_verify_only_needs_no_cue_and_creates_no_output(self):
        result, errors = self.run_patcher("--verify-only")
        self.assertEqual(result, 0, errors)
        self.assertFalse(self.output.exists())

    def test_wrong_bin_is_still_rejected(self):
        data = bytearray(self.source.read_bytes())
        data[0] ^= 1
        self.source.write_bytes(data)
        result, errors = self.run_patcher()
        self.assertEqual(result, 1)
        self.assertIn("source BIN is not the supported source file", errors)
        self.assertFalse(self.output.exists())

    def test_corrupt_patch_is_still_rejected(self):
        part = next((self.root / "patches").iterdir())
        data = bytearray(part.read_bytes())
        data[-1] ^= 1
        part.write_bytes(data)
        result, errors = self.run_patcher()
        self.assertEqual(result, 1)
        self.assertIn("patch part", errors)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
