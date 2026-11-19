"""
Permissions helper for the authority module (CW-303).

Creates the require_officer dependency that gates all authority endpoints.
Now delegates to platform require_role so the logic lives in one place.
"""
from backend.app.platform.deps import require_role

# Teammates import require_officer from this module; the name is kept the same
# so their imports and tests do not change.
require_officer = require_role("officer", "admin")
