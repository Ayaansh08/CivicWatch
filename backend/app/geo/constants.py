"""
Named constants for geospatial queries, density grids, and limits.
"""
# Maximum number of query results loaded into memory
MAX_RESULTS = 5000

# Default nearby search results limit
DEFAULT_NEARBY_LIMIT = 500

# Default spatial clustering cell size in degrees (~1.1 km)
DEFAULT_CELL_SIZE = 0.01

# Grid cell size in degrees for heatmap density overlay (~220 m)
HEATMAP_CELL_SIZE = 0.002

# Grid cell size in degrees for geographic report summary groupings
REPORT_CELL_SIZE = 0.01
