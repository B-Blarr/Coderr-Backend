"""Tests for the clear_expired_cache management command."""

from io import StringIO

from django.core.cache import cache
from django.core.management import CommandError, call_command
from django.db import connection
from django.test import TestCase, override_settings


class ClearExpiredCacheTests(TestCase):
    """The command removes expired cache rows and keeps valid ones."""

    def setUp(self):
        """Store one expired and one valid entry.

        A timeout of 0 makes the database cache write a row that has
        already expired, which is exactly what a throttle leaves behind.
        """
        cache.set('expired', 1, timeout=0)
        cache.set('valid', 1, timeout=60)

    def test_deletes_only_expired_rows(self):
        call_command('clear_expired_cache', stdout=StringIO())
        self.assertEqual(self._stored_keys(), [cache.make_key('valid')])

    def test_reports_the_number_of_deleted_rows(self):
        out = StringIO()
        call_command('clear_expired_cache', stdout=out)
        self.assertEqual(
            out.getvalue(), "Deleted 1 expired cache entries.\n")

    def test_refuses_a_cache_that_is_not_in_the_database(self):
        locmem = {'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
        with override_settings(CACHES=locmem):
            with self.assertRaises(CommandError):
                call_command('clear_expired_cache', stdout=StringIO())

    def _stored_keys(self):
        """Return the keys that are physically in the cache table."""
        with connection.cursor() as cursor:
            cursor.execute("SELECT cache_key FROM django_cache")
            return [row[0] for row in cursor.fetchall()]
