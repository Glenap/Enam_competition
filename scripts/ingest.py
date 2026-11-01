#!/usr/bin/env python3
"""Run from the repository root: python -m scripts.ingest [--ticker TCS]."""
import argparse
import json
import time
from finn.core import ROOT
from finn.ingestion import poll

if __name__ == '__main__':
 parser = argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--ticker', action='append', help='Repeat to select symbols; defaults to portfolio')
 parser.add_argument('--interval', type=int, default=0, help='Seconds between polls; 0 runs once, minimum 900 for a worker')
 args = parser.parse_args()
 if args.interval and args.interval < 900:
  parser.error('--interval must be 0 or at least 900')
 (ROOT / 'data').mkdir(exist_ok=True)
 while True:
  failures = poll(args.ticker)
  print(json.dumps({'failures': failures}), flush=True)
  if not args.interval:
   raise SystemExit(bool(failures))
  time.sleep(args.interval)
