"""Finite-diagram anchor audits; Python standard library only.

The default distances use discrete candidate-threshold matching in binary64.
The optional 'hera' backend uses GUDHI Hera with zero approximation parameter
and SciPy nearest neighbors. Neither is a formal exact-real or interval certificate.
Diagrams may contain repeated points and diagonal points, and may be empty.
Essential intervals (infinite coordinates) are deliberately unsupported.
"""

from .core import (
    MAX_ALTERNATES, MAX_DIAGRAM_POINTS, MAX_FAST_DIAGRAM_POINTS, MAX_STEPS, NUMERIC_SCOPE,
    audit_site, bottleneck, endpoint_bounds, hausdorff, interval_ranking, top_set,
)

__version__ = "0.1.0"
__all__ = [
    "audit_site", "bottleneck", "endpoint_bounds", "hausdorff",
    "interval_ranking", "top_set", "MAX_DIAGRAM_POINTS", "MAX_STEPS",
    "MAX_ALTERNATES", "MAX_FAST_DIAGRAM_POINTS", "NUMERIC_SCOPE",
]
