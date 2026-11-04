import logging

from django.core.management.base import BaseCommand, CommandError

from catalog.services.importer import import_medicines_csv

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import medicines from a CSV file (see sample_data/medicines_sample.csv)."

    def add_arguments(self, parser):
        parser.add_argument("path")
        parser.add_argument("--dry-run", action="store_true", help="Validate only; save nothing.")

    def handle(self, *args, **options):
        try:
            with open(options["path"], "rb") as fh:
                result = import_medicines_csv(fh, dry_run=options["dry_run"])
        except FileNotFoundError:
            raise CommandError(f"File not found: {options['path']}")
        label = "Would create" if options["dry_run"] else "Created"
        self.stdout.write(f"{label} {result.created}, updated {result.updated}.")
        for line, msg in result.errors:
            self.stderr.write(f"  line {line}: {msg}")
        if result.errors:
            raise CommandError(f"{len(result.errors)} row(s) had errors.")
