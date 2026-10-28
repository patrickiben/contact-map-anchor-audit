"""JSON-in / JSON-out command line interface."""

import argparse
import json
from pathlib import Path
import sys

from . import audit_site


def _reject_constant(value):
    raise ValueError(f"Nonstandard JSON numeric constant: {value}")


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON object key: {key}")
        result[key] = value
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Audit declared persistence-diagram anchor shifts (binary64; no map or PH reconstruction).")
    parser.add_argument("input", type=Path, help="JSON site or {\"sites\": [...]} batch")
    parser.add_argument("--output", type=Path, help="write JSON to a new file (otherwise stdout)")
    parser.add_argument("--steps", type=int, default=21)
    parser.add_argument("--tolerance", type=float, default=1e-6)
    parser.add_argument("--allowance", type=float, default=1e-12)
    parser.add_argument("--backend", choices=("reference", "hera"), default="reference",
                        help="reference: no dependencies, 128 points; hera: optional [fast] stack, 20,000 points")
    args = parser.parse_args(argv)
    try:
        if args.output is not None and args.output.resolve() == args.input.resolve():
            raise ValueError("Output must not overwrite the input file")
        if args.output is not None and args.output.exists():
            raise ValueError("Output already exists; choose a new path")
        data = json.loads(args.input.read_text(encoding="utf-8"), parse_constant=_reject_constant, object_pairs_hook=_unique_object)
        options = {"steps": args.steps, "tolerance": args.tolerance, "allowance": args.allowance, "backend": args.backend}
        if isinstance(data, dict) and "sites" in data:
            if not isinstance(data["sites"], list) or not data["sites"]:
                raise ValueError("sites must be a nonempty array")
            reports = [audit_site(site, **options) for site in data["sites"]]
            if len({report["id"] for report in reports}) != len(reports):
                raise ValueError("Batch site IDs must be unique")
            result = {"schema_version": "anchor-audit/batch-v1", "sites": reports}
        else:
            result = audit_site(data, **options)
        rendered = json.dumps(result, indent=2, allow_nan=False) + "\n"
        if args.output is None:
            sys.stdout.write(rendered)
        else:
            # Exclusive creation also protects against a file appearing after validation.
            with args.output.open("x", encoding="utf-8") as output:
                output.write(rendered)
        return 0
    except (ValueError, OSError) as exc:
        parser.exit(2, f"anchor-audit: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
