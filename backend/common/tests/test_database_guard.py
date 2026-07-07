from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from config.database_guard import validate_production_database


class ValidateProductionDatabaseTests(SimpleTestCase):
    def test_debug_true_allows_missing_database_url(self):
        validate_production_database(
            debug=True, database_url="", engine="django.db.backends.sqlite3"
        )

    def test_debug_true_allows_sqlite_engine(self):
        validate_production_database(
            debug=True,
            database_url="sqlite:///dev.sqlite3",
            engine="django.db.backends.sqlite3",
        )

    def test_debug_false_missing_database_url_raises(self):
        with self.assertRaises(ImproperlyConfigured):
            validate_production_database(
                debug=False, database_url="", engine="django.db.backends.postgresql"
            )

    def test_debug_false_whitespace_database_url_raises(self):
        with self.assertRaises(ImproperlyConfigured):
            validate_production_database(
                debug=False, database_url="   ", engine="django.db.backends.postgresql"
            )

    def test_debug_false_sqlite_engine_raises(self):
        with self.assertRaises(ImproperlyConfigured):
            validate_production_database(
                debug=False,
                database_url="sqlite:///prod.sqlite3",
                engine="django.db.backends.sqlite3",
            )

    def test_debug_false_postgres_passes(self):
        validate_production_database(
            debug=False,
            database_url="postgresql://user@db.example.supabase.co:5432/postgres",
            engine="django.db.backends.postgresql",
        )
