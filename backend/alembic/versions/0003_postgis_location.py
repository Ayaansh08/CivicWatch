"""
PostGIS geometry column, spatial indexes, and automatic sync trigger for complaints.

Revision ID: 0003_postgis_location
Revises: 0001_base
Create Date: 2026-11-16
"""
from alembic import op

# Revision identifiers used by Alembic
revision = "0003_postgis_location"
# TODO: change down_revision to 0002_status_history after teammate Ayan's migration is merged (avoid two Alembic heads)
down_revision = "0001_base"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add PostGIS geometry support, indexes, and sync trigger to complaints."""

    # 1. Enable the PostGIS spatial database extension if not already present
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

    # 2. Add nullable geometry Point column with SRID 4326 (WGS 84 GPS coordinates)
    op.execute("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS location geometry(Point, 4326);")

    # 3. Populate location for existing rows (note: ST_MakePoint takes longitude first, then latitude)
    op.execute(
        "UPDATE complaints "
        "SET location = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326) "
        "WHERE longitude IS NOT NULL AND latitude IS NOT NULL;"
    )

    # 4a. Create trigger function to sync location from longitude and latitude
    op.execute(
        """
        CREATE OR REPLACE FUNCTION sync_complaint_location()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Set location point with longitude first then latitude
            IF NEW.longitude IS NOT NULL AND NEW.latitude IS NOT NULL THEN
                NEW.location := ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326);
            ELSE
                NEW.location := NULL;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    # 4b. Create BEFORE trigger on insert or update of latitude and longitude
    op.execute(
        """
        CREATE TRIGGER trg_sync_complaint_location
        BEFORE INSERT OR UPDATE OF latitude, longitude ON complaints
        FOR EACH ROW
        EXECUTE FUNCTION sync_complaint_location();
        """
    )

    # 5. Create GiST spatial index on geometry location for fast bounding-box queries
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_complaints_location "
        "ON complaints USING GIST (location);"
    )

    # 6. Create GiST spatial index on geography-cast location for fast distance searches in metres
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_complaints_location_geog "
        "ON complaints USING GIST ((location::geography));"
    )


def downgrade() -> None:
    """Drop spatial indexes, trigger, trigger function, and geometry column in reverse order."""

    # 1. Drop geography GiST index
    op.execute("DROP INDEX IF EXISTS ix_complaints_location_geog;")

    # 2. Drop geometry GiST index
    op.execute("DROP INDEX IF EXISTS ix_complaints_location;")

    # 3. Drop location sync trigger from complaints table
    op.execute("DROP TRIGGER IF EXISTS trg_sync_complaint_location ON complaints;")

    # 4. Drop trigger function
    op.execute("DROP FUNCTION IF EXISTS sync_complaint_location();")

    # 5. Drop location geometry column from complaints table
    op.execute("ALTER TABLE complaints DROP COLUMN IF EXISTS location;")
