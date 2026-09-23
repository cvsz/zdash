"""Contract tests for the production environment fail-closed gate."""

import unittest

from verify_prod_env import validate


class ProductionEnvTests(unittest.TestCase):
    def setUp(self):
        self.values = {
            "APP_ENV": "production",
            "AUTH_ENABLED": "true",
            "AUTH_ALLOW_BOOTSTRAP_IN_PRODUCTION": "false",
            "PRODUCTION_SAFETY_LOCK": "true",
            "PRODUCTION_ALLOW_LIVE_ACTIONS": "false",
            "DRY_RUN": "true",
            "RISK_GUARDIAN_ENABLED": "true",
            "SOCIAL_DRY_RUN": "true",
            "SOCIAL_AUTO_POST_ENABLED": "false",
            "IOT_DRY_RUN": "true",
            "METRICS_AUTH_REQUIRED": "true",
            "JWT_SECRET_KEY": "J" * 48,
            "POSTGRES_PASSWORD": "P" * 32,
            "BOOTSTRAP_ADMIN_PASSWORD": "B" * 32,
            "API_KEY_HASH_PEPPER": "K" * 40,
            "DATABASE_URL": "postgresql+psycopg://zdash:" + "P" * 32 + "@postgres:5432/zdash",
            "FRONTEND_ORIGIN": "https://zdash.example.invalid",
            "CORS_ALLOW_ORIGINS": "https://zdash.example.invalid",
        }

    def test_accepts_explicit_safe_example(self):
        self.assertEqual(validate(self.values), [])

    def test_rejects_development_defaults_and_live_mutations(self):
        self.values.update({
            "AUTH_ENABLED": "false",
            "POSTGRES_PASSWORD": "zdash_dev_password",
            "PRODUCTION_ALLOW_LIVE_ACTIONS": "true",
        })
        problems = validate(self.values)
        self.assertTrue(any("AUTH_ENABLED" in x for x in problems))
        self.assertTrue(any("POSTGRES_PASSWORD" in x for x in problems))
        self.assertTrue(any("PRODUCTION_ALLOW_LIVE_ACTIONS" in x for x in problems))

    def test_rejects_wildcard_or_insecure_cors(self):
        self.values["CORS_ALLOW_ORIGINS"] = "*"
        self.assertTrue(any("CORS_ALLOW_ORIGINS" in x for x in validate(self.values)))


if __name__ == "__main__":
    unittest.main()
