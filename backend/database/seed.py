"""Load Git-tracked source data into an initialized database.

Kept for backwards compatibility with ``python -m backend.database.init_db
--seed``. Development seeding and Git-tracked source synchronization share the
same idempotent upsert path defined in :mod:`backend.database.sync_data`; the
tracked ``data/`` files are the authoritative source.
"""


def seed_database(connection) -> None:
    """Upsert the committed source data so seeding can safely be repeated."""
    # Import lazily because sync_data imports initialize_database.
    from .sync_data import sync_source_data

    sync_source_data(connection)
