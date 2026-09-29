"""Management command that deletes expired rows from the database cache."""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.utils import timezone

DATABASE_CACHE = 'django.core.cache.backends.db.DatabaseCache'


class Command(BaseCommand):
    """Deletes cache rows whose expiry date has passed.

    Django's database cache removes an expired row only when that key is
    read again or when the table holds more than MAX_ENTRIES rows. The
    throttles key their rows by client address, so without this command
    the addresses of visitors who never return stay in the table.
    """

    help = "Delete expired rows from the database cache table."

    def handle(self, *args, **options):
        """Delete every expired row and report how many there were."""
        table = connection.ops.quote_name(self._table_name())
        expires = connection.ops.quote_name('expires')
        now = connection.ops.adapt_datetimefield_value(timezone.now())
        with connection.cursor() as cursor:
            cursor.execute(
                f"DELETE FROM {table} WHERE {expires} < %s", [now])
            deleted = cursor.rowcount
        self.stdout.write(f"Deleted {deleted} expired cache entries.")

    def _table_name(self):
        """Return the cache table, or stop if no database cache is used."""
        config = settings.CACHES['default']
        if config['BACKEND'] != DATABASE_CACHE:
            raise CommandError("The default cache is not a database cache.")
        return config['LOCATION']
