#!/usr/bin/env python3
"""Run from the repository root: python -m scripts.ingest [--ticker TCS]."""
import argparse
import json
import threading
from finn.ingestion import poll, run_worker

if __name__ == '__main__':
 parser = argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--ticker', action='append', help='Repeat to select symbols; defaults to portfolio')
 parser.add_argument('--interval', type=int, default=0, help='Seconds between polls; 0 runs once, minimum 900 for a worker')
 args = parser.parse_args()
 if args.interval and args.interval < 900:
  parser.error('--interval must be 0 or at least 900')
 if args.interval:
  stop = threading.Event()
  try:
   run_worker(args.interval, stop, args.ticker)
  except KeyboardInterrupt:
   stop.set()
 else:
  failures = poll(args.ticker)
  print(json.dumps({'failures': failures}), flush=True)
  raise SystemExit(bool(failures))
