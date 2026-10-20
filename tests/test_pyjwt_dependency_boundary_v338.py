"""Dependency contract regression tests for the zDash PyJWT security upgrade."""
import os
from pathlib import Path
import re
import tomllib
import unittest

from packaging.requirements import Requirement
from packaging.version import Version

ROOT = Path(os.environ.get("ZDASH_CHECKOUT", Path(__file__).resolve().parents[1]))
MINIMUM = Version("2.15.1")
LOCKS = ("backend/requirements.lock", "backend/requirements-dev.lock")
SPECS = ("backend/requirements.txt", "backend/pyproject.toml")


def jwt_requirement(text):
    requirements = [Requirement(line.strip()) for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    found = [item for item in requirements if item.name.lower() == "pyjwt"]
    if len(found) != 1:
        raise AssertionError(f"expected exactly one PyJWT requirement; got {len(found)}")
    return found[0]


class DependencyBoundaryTests(unittest.TestCase):
    def test_runtime_lock_exact_safe_version(self):
        self.assertEqual(str(jwt_requirement((ROOT / LOCKS[0]).read_text()).specifier), "==2.15.1")

    def test_dev_lock_exact_safe_version(self):
        self.assertEqual(str(jwt_requirement((ROOT / LOCKS[1]).read_text()).specifier), "==2.15.1")

    def test_runtime_spec_requires_safe_version(self):
        requirement = jwt_requirement((ROOT / SPECS[0]).read_text())
        self.assertIn(MINIMUM, requirement.specifier)
        self.assertNotIn(Version("2.13.0"), requirement.specifier)
        self.assertNotIn(Version("2.15.0"), requirement.specifier)

    def test_pyproject_spec_requires_safe_version(self):
        parsed = tomllib.loads((ROOT / SPECS[1]).read_text())
        requirements = [Requirement(s) for s in parsed["project"]["dependencies"]]
        matching = [r for r in requirements if r.name.lower() == "pyjwt"]
        self.assertEqual(len(matching), 1)
        self.assertIn(MINIMUM, matching[0].specifier)
        self.assertNotIn(Version("2.13.0"), matching[0].specifier)
        self.assertNotIn(Version("2.15.0"), matching[0].specifier)

    def test_locks_consistent(self):
        self.assertEqual(*(str(jwt_requirement((ROOT / p).read_text()).specifier) for p in LOCKS))

    def test_no_other_runtime_dependencies_changed(self):
        for p in LOCKS:
            lines = (ROOT / p).read_text().splitlines()
            self.assertTrue(all("==" in line for line in lines if line and not line.startswith("#")))
            self.assertEqual(len(lines), len(set(lines)))

    def test_supported_python(self):
        parsed = tomllib.loads((ROOT / SPECS[1]).read_text())
        self.assertEqual(parsed["project"]["requires-python"], ">=3.11")

    def test_hmac_token_compatibility_smoke_installed_package(self):
        # Smoke only: local PyJWT may be older than candidate; does not certify upgraded wheel.
        import jwt
        key = "nonproduction-test-key-at-least-32-bytes-for-hmac"
        token = jwt.encode({"sub": "test", "iss": "test-suite"}, key, algorithm="HS256")
        decoded = jwt.decode(token, key, algorithms=["HS256"], issuer="test-suite")
        self.assertEqual(decoded["sub"], "test")
        with self.assertRaises(jwt.InvalidSignatureError):
            jwt.decode(token, "wrong-key-at-least-32-bytes-for-hmac-abcdef", algorithms=["HS256"], issuer="test-suite")
        with self.assertRaises(jwt.InvalidAlgorithmError):
            jwt.decode(token, key, algorithms=["HS384"], issuer="test-suite")


if __name__ == "__main__":
    unittest.main()
