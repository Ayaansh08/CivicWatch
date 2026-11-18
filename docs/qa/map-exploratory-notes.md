# Map Module Exploratory Testing Notes (CW-410)

**Tester:** Ayaansh (M4, Geospatial and Analytics)  
**Date:** November 2026  
**Target:** CivicWatch Geospatial & Map Module (Sprint 3)

---

## Charter 1: Marker Loading & Display

**Objective:** Verify that complaints inside the visible bounding box load and display correctly on the map.

| Test Scenario | Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| Initial map marker load | Navigate to `/map` as an authorized officer | Map centers on Noida (28.62, 77.36); bounding box query executes with auth token; total count message and markers appear | TODO | TODO |
| Marker popup inspection | Click on a visible complaint marker | Popup opens showing sanitized title, category, status, and priority; HTML script injection is prevented | TODO | TODO |

---

## Charter 2: Marker Clustering Behavior

**Objective:** Validate that marker clustering groups nearby complaint pins dynamically based on map zoom level.

| Test Scenario | Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| Clustering at low zoom | Zoom out to see regional NCR view (zoom level 10-12) | Nearby markers collapse into cluster circles showing complaint counts | TODO | TODO |
| Cluster spiderfy and expansion | Click a cluster circle or zoom in (zoom level 15+) | Cluster expands / spiderfies into individual complaint pins | TODO | TODO |

---

## Charter 3: Map Filtering (Category & Status)

**Objective:** Verify that category and status filters update the displayed complaints and summary messages.

| Test Scenario | Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| Filter by category | Select a specific category (e.g., 'Pothole') from the category dropdown | Only complaints matching that category ID are rendered on the map | TODO | TODO |
| Filter by status | Select a status (e.g., 'In Progress') from the status dropdown | Only complaints with the chosen status are displayed | TODO | TODO |
| Combined filters | Select both a category and a status | Only complaints matching both criteria are shown | TODO | TODO |
| Clear filters | Click 'Clear filters' button | Category and status dropdowns reset; all box complaints reload | TODO | TODO |

---

## Charter 4: Heatmap Toggle & Density Rendering

**Objective:** Verify switching between marker clustering and density heatmap layer.

| Test Scenario | Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| Heatmap view toggle | Click 'Heatmap' button in the toolbar | Marker cluster layer is removed; leaflet.heat density overlay renders with gradient color intensity | TODO | TODO |
| Filtered heatmap | Apply category or status filters while in Heatmap mode | Heatmap cells recalculate and reflect the filtered complaint density | TODO | TODO |
| Return to markers | Click 'Markers' button in the toolbar | Heatmap layer is cleared; clustered markers return | TODO | TODO |

---

## Charter 5: Edge Cases & Network Resilience

**Objective:** Test map behavior in empty areas, API errors, slow networks, and unauthorized access attempts.

| Test Scenario | Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| Empty bounding box area | Pan or filter to a region with zero complaints | Displays message "No complaints found in this area" or "No complaints match these filters" without crashing | TODO | TODO |
| Backend API error (500) | Simulate backend failure or 500 response | Map container renders; red error message "Could not load complaints" is shown | TODO | TODO |
| Slow network (3G simulation) | Throttle network to Slow 3G in browser dev tools | "Loading complaints..." message appears during fetch; UI remains responsive | TODO | TODO |
| Citizen access restriction | Log in as a citizen user and attempt to access `/map` or `/geo/heatmap` | Frontend route redirects or backend returns HTTP 403 Forbidden ("You do not have permission to do this") | TODO | TODO |
