#!/usr/bin/env python3
"""Prepare an explicitly new replay freeze; never make a model/API request."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        raise SystemExit('Replay output must not exist; preserve all historical/frozen runs.')
    out = args.output.resolve()
    (out / 'scripts').mkdir(parents=True)
    for name in ('candidate_cohort.json', 'midpoint_selection.json'):
        shutil.copy2(ROOT / 'provenance' / name, out / name)
    shutil.copy2(ROOT / 'analysis_source/portability/scripts/acquire_portability.py', out / 'scripts/acquire_portability.py')
    (out / 'REPLAY_PROTOCOL.md').write_text(
        '# Re-acquisition replay protocol\n\n'
        'This is a new replay of the historically frozen cohort and paired track request. '
        'It is not the original prospective experiment and creates no new prospective claim. '
        'The API may change; compare every saved output to the original exact-input controls. '
        'Keep the historic native predictions and results unchanged. '
        'Use the same allele order and both specified tracks; retain failures and all returned arrays. '
        'Credentials are supplied externally. Model inference occurs only when the separate '
        'acquisition command is explicitly run without --check-only.\n')
    files = ['scripts/acquire_portability.py', 'candidate_cohort.json', 'midpoint_selection.json', 'REPLAY_PROTOCOL.md']
    record = {'artifact_type':'new_reacquisition_replay_freeze',
        'frozen_utc':datetime.now(timezone.utc).isoformat(), 'protocol_file':'REPLAY_PROTOCOL.md',
        'original_historical_freeze_replaced':False,
        'files':{n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in files}}
    (out/'freeze_record.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':'REPLAY_PREPARED_NO_REQUESTS','network_calls':0,'files_frozen':len(files)}))


if __name__ == '__main__':
    main()
