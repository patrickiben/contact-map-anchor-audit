"""A transparent small-diagram reference implementation of the anchor audit."""

from collections.abc import Mapping
from functools import lru_cache
import math

MAX_DIAGRAM_POINTS = 128
MAX_FAST_DIAGRAM_POINTS = 20_000
MAX_ALTERNATES = 32
MAX_STEPS = 1001
NUMERIC_SCOPE = (
    "Binary64 finite-diagram matching; allowance is a user-supplied practical "
    "error budget, not a proved arithmetic enclosure. Ranking guarantees are "
    "conditional on valid bounds. No exact-real certification or biological validation."
)


def _backend_cap(backend):
    if backend == "reference":
        return MAX_DIAGRAM_POINTS
    if backend == "hera":
        return MAX_FAST_DIAGRAM_POINTS
    raise ValueError("backend must be 'reference' or 'hera'")


@lru_cache(maxsize=1)
def _fast_modules():
    try:
        import gudhi
        import gudhi.hera
        import numpy
        import scipy
        from scipy.spatial import cKDTree
    except ImportError as exc:
        raise ValueError("The hera backend requires optional dependencies. On Python >=3.12 with compatible platform wheels, install 'contact-map-anchor-audit[fast]'.") from exc
    return gudhi, numpy, scipy, cKDTree


def _backend_metadata(backend):
    _backend_cap(backend)
    if backend == "reference":
        return {"name": "reference", "libraries": {}}
    gudhi, numpy, scipy, _ = _fast_modules()
    return {"name": "hera", "libraries": {
        "gudhi": gudhi.__version__, "numpy": numpy.__version__, "scipy": scipy.__version__}}


def _number(value, name, nonnegative=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    try:
        value = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} is outside binary64 range") from exc
    if not math.isfinite(value) or (nonnegative and value < 0):
        raise ValueError(f"{name} must be finite" + (" and nonnegative" if nonnegative else ""))
    return value


def _finite(value):
    if not math.isfinite(value):
        raise ValueError("Computation overflowed; rescale diagram coordinates and shifts")
    return value


def _diagram(value, name="diagram", backend="reference"):
    cap = _backend_cap(backend)
    if not isinstance(value, (list, tuple)) or len(value) > cap:
        raise ValueError(f"{name} must be an array of at most {cap} points for backend {backend}")
    result = []
    for index, point in enumerate(value):
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            raise ValueError(f"{name}[{index}] must be [birth, death]")
        birth = _number(point[0], f"{name}[{index}].birth")
        death = _number(point[1], f"{name}[{index}].death")
        if birth > death:
            raise ValueError(f"{name}[{index}] has birth greater than death")
        _finite(death - birth)
        result.append((birth, death))
    return result


def _cost(x, y):
    return _finite(max(abs(x[0] - y[0]), abs(x[1] - y[1])))


def _diagonal(x):
    return _finite(x[1] - x[0]) / 2


def _finite_pair_extent(D, E):
    """Reject overflowing pairwise differences in O(n+m) space/time."""
    if D and E:
        for coordinate in (0, 1):
            _finite(max(p[coordinate] for p in D)-min(p[coordinate] for p in E))
            _finite(max(p[coordinate] for p in E)-min(p[coordinate] for p in D))


def bottleneck(D, E, *, backend="reference"):
    """Return finite persistence bottleneck distance, including the diagonal.

    Uses the standard augmented (n+m)-vertex bipartite perfect-matching test.
    Binary search is over *all* distinct candidate costs, with no approximation
    tolerance in the matching decisions. Float arithmetic still incurs rounding.
    Worst-case O((n+m)^3 log(n+m)) time, O((n+m)^2) memory. Each input is
    limited to MAX_DIAGRAM_POINTS. Multiplicity is retained. backend='hera'
    instead uses optional GUDHI Hera with delta=0 and allows 20,000 points per
    diagram, without constructing a dense pairwise cost matrix in Python.
    """
    D, E = _diagram(D, "D", backend), _diagram(E, "E", backend)
    if backend == "hera":
        gudhi, np, _, _ = _fast_modules()
        _finite_pair_extent(D, E)
        # Hera does not support diagonal points. Removing only these zero-cost
        # points preserves persistence distance; repeated off-diagonal points stay.
        D, E = [p for p in D if p[0] < p[1]], [p for p in E if p[0] < p[1]]
        if not D:
            return max((_diagonal(y) for y in E), default=0.0)
        if not E:
            return max((_diagonal(x) for x in D), default=0.0)
        result = float(gudhi.hera.bottleneck_distance(np.asarray(D, dtype=float), np.asarray(E, dtype=float), delta=0.0))
        return _number(result, "Hera bottleneck result", True)
    n, m = len(D), len(E)
    if not n:
        return max((_diagonal(y) for y in E), default=0.0)
    if not m:
        return max((_diagonal(x) for x in D), default=0.0)
    # Left: D and E-diagonal copies; right: E and D-diagonal copies.
    # Only a real point's own diagonal copy is needed; dummy-dummy edges
    # complete unused copies at zero cost, encoding unlimited diagonal supply.
    edges = []
    for i, x in enumerate(D):
        edges.append([(j, _cost(x, y)) for j, y in enumerate(E)] + [(m+i, _diagonal(x))])
    for j, y in enumerate(E):
        edges.append([(j, _diagonal(y))] + [(m+i, 0.0) for i in range(n)])
    candidates = sorted({cost for row in edges for _, cost in row})

    def feasible(threshold):
        adjacent = [[j for j, cost in row if cost <= threshold] for row in edges]
        owners = [-1] * (n+m)

        def augment(left, seen):
            for right in adjacent[left]:
                if seen[right]:
                    continue
                seen[right] = True
                if owners[right] == -1 or augment(owners[right], seen):
                    owners[right] = left
                    return True
            return False

        return all(augment(left, [False] * (n+m)) for left in range(n+m))

    low, high = 0, len(candidates)-1
    while low < high:
        middle = (low+high)//2
        if feasible(candidates[middle]):
            high = middle
        else:
            low = middle+1
    return candidates[low]


def hausdorff(D, E, *, backend="reference"):
    """Diagonal-augmented Hausdorff lower bound; does not enforce multiplicity.

    backend='hera' uses cKDTree with p=infinity and eps=0, avoiding a dense
    pairwise distance array. It shares the fast backend's optional dependencies.
    """
    D, E = _diagram(D, "D", backend), _diagram(E, "E", backend)
    if backend == "hera":
        _, np, _, cKDTree = _fast_modules()
        _finite_pair_extent(D, E)

        def fast_directed(points, opposite):
            if not points:
                return 0.0
            if not opposite:
                return max(_diagonal(x) for x in points)
            array = np.asarray(points, dtype=float)
            nearest, _ = cKDTree(np.asarray(opposite, dtype=float)).query(array, k=1, p=np.inf, eps=0.0)
            if not np.isfinite(nearest).all():
                raise ValueError("Nonfinite nearest-neighbor calculation; rescale coordinates")
            diagonal = (array[:, 1]-array[:, 0])/2
            return _number(float(np.minimum(nearest, diagonal).max()), "Hausdorff result", True)

        return max(fast_directed(D, E), fast_directed(E, D))

    def directed(points, opposite):
        return max((min(_diagonal(x), min((_cost(x, y) for y in opposite), default=math.inf))
                    for x in points), default=0.0)

    return max(directed(D, E), directed(E, D))


def endpoint_bounds(A, C, delta, lam, error=0):
    """Return (lower, upper) endpoint cones at lambda=lam in [0,1].

    error is a common absolute endpoint-error budget. Mathematical enclosures
    require that budget to cover input, shift, translation and solver errors.
    This function does not prove the supplied budget valid.
    """
    A, C = _number(A, "A", True), _number(C, "C", True)
    T = abs(_number(delta, "delta"))
    lam, error = _number(lam, "lambda"), _number(error, "error", True)
    if not 0 <= lam <= 1:
        raise ValueError("lambda must be between 0 and 1")
    lower = max(0.0, _finite(A-error-lam*T), _finite(C-error-(1-lam)*T))
    upper = min(_finite(A+error+lam*T), _finite(C+error+(1-lam)*T))
    if lower > upper:
        raise ValueError("Inconsistent endpoint bounds; endpoints violate the shift/error budget")
    return lower, upper


def _scores(values, name):
    if not isinstance(values, Mapping) or not values:
        raise ValueError(f"{name} must be a nonempty mapping from IDs to scores")
    return {key: _number(value, f"{name}[{key!r}]") for key, value in values.items()}


def top_set(scores, tolerance=1e-6):
    """Return IDs whose score is within tolerance (inclusive) of the maximum."""
    scores, tolerance = _scores(scores, "scores"), _number(tolerance, "tolerance", True)
    maximum = max(scores.values())
    return [key for key, value in scores.items() if value >= _finite(maximum-tolerance)]


def interval_ranking(lower, upper, tolerance=1e-6):
    """Possible/guaranteed top membership for Cartesian score intervals.

    guaranteed_unique requires a gap strictly greater than tolerance against
    every competitor. For one alternative, all three sets contain that ID.
    All guarantees are conditional on the intervals being valid enclosures.
    """
    lower, upper = _scores(lower, "lower"), _scores(upper, "upper")
    tolerance = _number(tolerance, "tolerance", True)
    if lower.keys() != upper.keys() or any(lower[k] > upper[k] for k in lower):
        raise ValueError("Interval mappings must have identical keys and lower <= upper")
    possible, guaranteed, unique = [], [], []
    for key in lower:
        others = [other for other in lower if other != key]
        if not others:
            possible.append(key)
            guaranteed.append(key)
            unique.append(key)
            continue
        max_lower, max_upper = max(lower[k] for k in others), max(upper[k] for k in others)
        if upper[key] >= _finite(max_lower-tolerance):
            possible.append(key)
        if lower[key] >= _finite(max_upper-tolerance):
            guaranteed.append(key)
        if lower[key] > _finite(max_upper+tolerance):
            unique.append(key)
    return {"possible": possible, "guaranteed": guaranteed, "guaranteed_unique": unique}


def _identifier(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty string")
    return value


def audit_site(site, steps=21, tolerance=1e-6, allowance=1e-12, *, backend="reference"):
    """Audit one site with supplied finite diagrams and ALT-minus-REF shifts.

    Each sampled distance is recomputed by matching; no linear interpolation
    is substituted for distance evaluation. Per-alternative lower/upper predict
    the centered distance from the native score, shift and centered Hausdorff
    witness. Path lower/upper use both computed endpoints. Neither requires a
    claim of endpoint saturation. No PH or map reconstruction is performed.
    backend='hera' requires the optional fast dependency stack (Python >=3.12
    for the pinned versions) and raises the per-diagram limit to 20,000.
    """
    if not isinstance(site, Mapping):
        raise ValueError("site must be an object")
    if isinstance(steps, bool) or not isinstance(steps, int) or not 2 <= steps <= MAX_STEPS:
        raise ValueError(f"steps must be an integer between 2 and {MAX_STEPS}")
    tolerance = _number(tolerance, "tolerance", True)
    allowance = _number(allowance, "allowance", True)
    doubled_allowance = _finite(2*allowance)
    backend_metadata = _backend_metadata(backend)
    site_id = _identifier(site.get("id"), "site.id")
    reference = _diagram(site.get("reference"), "reference", backend)
    raw_alternates = site.get("alternates")
    if not isinstance(raw_alternates, list) or not 1 <= len(raw_alternates) <= MAX_ALTERNATES:
        raise ValueError(f"alternates must contain 1 to {MAX_ALTERNATES} alternatives")
    alternates, ids = [], set()
    for alternate in raw_alternates:
        if not isinstance(alternate, Mapping):
            raise ValueError("each alternate must be an object")
        key = _identifier(alternate.get("id"), "alternate.id")
        if key in ids:
            raise ValueError(f"duplicate alternate ID: {key}")
        ids.add(key)
        alternates.append((key, _diagram(alternate.get("diagram"), key, backend), _number(alternate.get("delta"), "delta")))
    selected = site.get("selected")
    if selected is not None and (not isinstance(selected, str) or selected not in ids):
        raise ValueError("selected must name an alternate ID or be null")

    results = []
    warnings = ["Synthetic or user-supplied diagrams only; this audit does not establish clinical or biological validity.",
                "Practical numerical allowances are not formal arithmetic certificates; near saturation does not prove exact affinity."]
    for key, diagram, delta in alternates:
        if 0 < abs(delta) <= doubled_allowance:
            warnings.append(f"{key}: the nonzero shift is no larger than twice the allowance; numerical near-saturation is low-information at this error budget.")
        def shifted(lam):
            shift = _finite(lam*delta)

            def checked_add(coordinate):
                # TwoSum recovers the rounding residual of this one addition.
                # It does not certify the shift multiplication or the solver.
                total = _finite(coordinate+shift)
                virtual_shift = _finite(total-coordinate)
                virtual_coordinate = _finite(total-virtual_shift)
                residual = _finite((coordinate-virtual_coordinate)+(shift-virtual_shift))
                if abs(residual) > allowance:
                    raise ValueError("Translation rounding exceeds allowance; rescale coordinates or justify a larger error budget")
                return total

            translated = []
            for birth, death in diagram:
                new_birth, new_death = checked_add(birth), checked_add(death)
                lifetime_change = _finite(_finite(new_death-new_birth)-(death-birth))
                if abs(lifetime_change) > doubled_allowance:
                    raise ValueError("Translation changed a represented lifetime beyond twice the allowance; rescale coordinates or justify a larger error budget")
                translated.append((new_birth, new_death))
            return translated

        A = bottleneck(reference, diagram, backend=backend)
        centered_diagram = shifted(1.0)
        C = bottleneck(reference, centered_diagram, backend=backend)
        H = hausdorff(reference, centered_diagram, backend=backend)
        T, change = abs(delta), _finite(C-A)
        residual = _finite(T-abs(change))
        lower = max(0.0, _finite(A-T-allowance), _finite(H-allowance))
        upper = _finite(A+T+allowance)
        if lower > upper:
            raise ValueError("Native witness bounds are inconsistent at the supplied allowance; rescale inputs or justify a larger budget")
        path = []
        for index in range(steps):
            lam = index/(steps-1)
            distance = A if index == 0 else C if index == steps-1 else bottleneck(reference, shifted(lam), backend=backend)
            low, high = endpoint_bounds(A, C, delta, lam, allowance)
            if distance < low or distance > high:
                warnings.append(f"{key}: sampled distance at lambda={lam:g} falls outside endpoint bounds at the supplied allowance.")
            path.append({"lambda": lam, "distance": distance, "lower": low, "upper": high})
        results.append({"id": key, "delta": delta, "native": A, "centered": C,
                        "change": change, "absolute_shift": T, "saturation_residual": residual,
                        "near_saturated": abs(residual) <= doubled_allowance,
                        "hausdorff": H, "lower": lower, "upper": upper, "path": path})
    native = {a["id"]: a["native"] for a in results}
    centered = {a["id"]: a["centered"] for a in results}
    native_top, centered_top = top_set(native, tolerance), top_set(centered, tolerance)
    intervals = interval_ranking({a["id"]: a["lower"] for a in results}, {a["id"]: a["upper"] for a in results}, tolerance)
    margin_leaders = [a["id"] for a in results if all(
        _finite(a["native"]-b["native"]) > _finite(a["absolute_shift"]+b["absolute_shift"]+tolerance+2*allowance)
        for b in results if b["id"] != a["id"])]
    return {"schema_version": "anchor-audit/report-v1", "id": site_id,
            "backend": backend_metadata,
            "numeric_scope": NUMERIC_SCOPE, "tolerance": tolerance, "allowance": allowance,
            "selected": selected, "alternatives": results,
            "rankings": {"native": native_top, "centered": centered_top,
                         "possible_centered": intervals["possible"], "guaranteed_centered": intervals["guaranteed"],
                         "guaranteed_unique_centered": intervals["guaranteed_unique"],
                         "native_margin_leaders": margin_leaders},
            "credits": None if selected is None else {
                "native": 1/len(native_top) if selected in native_top else 0.0,
                "centered": 1/len(centered_top) if selected in centered_top else 0.0},
            "warnings": warnings}
