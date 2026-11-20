"""
Geo feature permissions.
Restricts advanced geospatial endpoints (heatmap, hotspots, reports)
to authority officers and platform administrators.
Delegates to platform require_role so the logic lives in one place.
"""
from backend.app.platform.deps import require_role

# Teammates import require_officer from this module; the name is kept the same
# so their imports and tests do not change.
require_officer = require_role("officer", "admin")
