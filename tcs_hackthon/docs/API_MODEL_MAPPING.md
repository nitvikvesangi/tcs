# Model to API Mapping

This document describes exactly how models and logic are extracted from Person 1/3 and mapped to the backend.

------------------------------------------------------------

DATA

Source:
`backend/data_loader.py`

Function:
`query_products()`

Used by:
`/recommendations`

Notes:
Since no raw `.csv` or Person 1 codebase was provided in the repository, the data layer utilizes an exported version of the mock recommendations containing pre-calculated AI options and states as the underlying dataset `backend/data/dataset.json`.

------------------------------------------------------------

INVENTORY

Source:
`backend/inventory_engine.py`

Function:
`calculate_inventory_alert()`

Used by:
`/recommendations`
`/inventory`

Notes:
Extracts the `inventory_snapshot` from the dataset row or falls back to a calculated threshold.

------------------------------------------------------------

PROMOTION

Source:
`backend/promotion_engine.py`

Function:
`generate_promotion_options()`

Used by:
`/recommendations`
`/promotions`

Notes:
Extracts the `recommendation` decisions and interactive `options` arrays.

------------------------------------------------------------

AI

Source:
`backend/ai_engine.py`

Function:
`generate_explanation()`
`generate_risk_flag()`

Used by:
`/recommendations`
`/chat`

Notes:
Since no `.pkl` files or ML components were found in the workspace, these functions simulate AI inference by extracting the pre-generated `reasons` and `risk_flag` from the data.

------------------------------------------------------------

MODEL

Source:
No `.pkl`, `.h5`, or `.joblib` model files exist in the repository.

Loader:
N/A

Used by:
N/A (Business logic relies on dataset heuristics to maintain 100% stable demo behavior)

------------------------------------------------------------
