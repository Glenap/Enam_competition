"""Durable live snapshots and a restart-safe portfolio polling entry point."""
import datetime as dt
import hashlib
import json
from .core import db, ticker, PORTFOLIO
from . import providers


def storage(path=None):
 con = db(path)
 con.executescript('''
 CREATE TABLE IF NOT EXISTS live_items (
  kind TEXT, ticker TEXT, identity TEXT, timestamp TEXT, payload TEXT,
  PRIMARY KEY(kind,ticker,identity));
 CREATE INDEX IF NOT EXISTS live_items_window ON live_items(kind,timestamp);
 CREATE TABLE IF NOT EXISTS ingestion_status (
  kind TEXT, ticker TEXT, attempted TEXT, succeeded TEXT, error TEXT,
  PRIMARY KEY(kind,ticker));
 ''')
 return con


def ingest(symbol, kind, path=None, price=4, volume=2):
 symbol = ticker(symbol).removesuffix('.NS')
 if kind not in ('announcements', 'prices'):
  raise ValueError('Unsupported ingestion kind')
 now = dt.datetime.now(dt.timezone.utc).isoformat()
 try:
  data = providers.announcements(symbol) if kind == 'announcements' else providers.prices(symbol, price, volume)
  records = data if kind == 'announcements' else [dict(bar, source=data['source'], currency=data.get('currency')) for bar in data['bars']]
  validated = []
  for record in records:
   timestamp = record.get('timestamp') if kind == 'announcements' else record.get('as_of')
   if not timestamp or dt.datetime.fromisoformat(timestamp).tzinfo is None:
    raise ValueError('Source record requires a timezone-aware timestamp')
   if not record.get('source', '').startswith('https://'):
    raise ValueError('Source record requires an HTTPS citation')
   # Stable content fallback avoids using response position as an exchange ID.
   identity = record.get('id') if kind == 'announcements' else timestamp
   if not identity:
    identity = hashlib.sha256((timestamp + record['title'] + record['source']).encode()).hexdigest()
   stored_time = dt.datetime.fromisoformat(timestamp).astimezone(dt.timezone.utc).isoformat()
   validated.append((kind, symbol, str(identity), stored_time, json.dumps(dict(record, ticker=symbol, demo=False))))
  with storage(path) as con:
   con.executemany('INSERT OR REPLACE INTO live_items VALUES (?,?,?,?,?)', validated)
   con.execute('INSERT OR REPLACE INTO ingestion_status VALUES (?,?,?,?,NULL)', (kind, symbol, now, now))
  return data
 except Exception:
  with storage(path) as con:
   con.execute('''INSERT INTO ingestion_status VALUES (?,?,?,NULL,?)
    ON CONFLICT(kind,ticker) DO UPDATE SET attempted=excluded.attempted,error=excluded.error''',
    (kind, symbol, now, 'Source unavailable or unsupported response; retained previous records.'))
  raise


def digest(path=None, hours=168):
 now = dt.datetime.now(dt.timezone.utc)
 cutoff = now - dt.timedelta(hours=hours)
 with storage(path) as con:
  rows = con.execute("SELECT payload FROM live_items WHERE kind='announcements' AND timestamp>=? AND timestamp<=?", (cutoff.isoformat(), now.isoformat())).fetchall()
  status = [dict(row) for row in con.execute('SELECT * FROM ingestion_status ORDER BY ticker,kind')]
 items = [json.loads(row['payload']) for row in rows]
 universe = {symbol for symbol, _, _ in PORTFOLIO}
 status = [entry for entry in status if entry['ticker'] in universe]
 items = [item for item in items if item['ticker'] in universe and cutoff <= dt.datetime.fromisoformat(item['timestamp']) <= now]
 items.sort(key=lambda item: (item['priority'], item['timestamp']), reverse=True)
 return {'mode': 'live', 'items': items, 'ingestion': status, 'as_of': now.isoformat()}


def poll(symbols=None, path=None, stop_event=None):
 failures = []
 for symbol in symbols or [row[0] for row in PORTFOLIO]:
  for kind in ('announcements', 'prices'):
   if stop_event is not None and stop_event.is_set():
    return failures
   try:
    ingest(symbol, kind, path)
   except Exception:
    failures.append({'ticker': symbol, 'kind': kind})
 return failures


def run_worker(interval, stop_event, symbols=None, path=None):
 """Poll immediately, then wait interruptibly; keep upstream failures isolated."""
 if interval < 900:
  raise ValueError('Polling interval must be at least 900 seconds')
 while not stop_event.is_set():
  failures = poll(symbols, path, stop_event)
  print(json.dumps({'ingestion_failures': failures}), flush=True)
  if stop_event.wait(interval):
   break
