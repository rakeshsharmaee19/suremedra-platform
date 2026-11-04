from django.db import migrations


def create_extension(apps, schema_editor):
    # Typo-tolerant search uses PostgreSQL's pg_trgm. Other databases (SQLite in dev) skip this.
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")


class Migration(migrations.Migration):
    dependencies = [("catalog", "0001_initial")]
    operations = [migrations.RunPython(create_extension, migrations.RunPython.noop)]
