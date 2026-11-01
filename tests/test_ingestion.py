import datetime as dt
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from finn.ingestion import ingest, digest, storage


class IngestionTests(unittest.TestCase):
 def setUp(self):
  self.temp = tempfile.TemporaryDirectory()
  self.addCleanup(self.temp.cleanup)
  self.path = Path(self.temp.name) / 'live.sqlite'
  self.now = dt.datetime.now(dt.timezone.utc)

 def filing(self, identity='123', hours=1, symbol='TCS'):
  return dict(id=identity, ticker=symbol, timestamp=(self.now-dt.timedelta(hours=hours)).isoformat(),
              title='Financial results', source='https://nsearchives.nseindia.com/test.pdf',
              category='Results', priority=90, demo=False)

 def test_restart_deduplication_and_windows(self):
  with patch('finn.providers.announcements', return_value=[self.filing(), self.filing('old', 60), self.filing('future', -1)]):
   ingest('TCS.NS', 'announcements', self.path)
   ingest('TCS', 'announcements', self.path)
  with storage(self.path) as con:
   self.assertEqual(con.execute('SELECT count(*) FROM live_items').fetchone()[0], 3)
  result = digest(self.path, hours=48)
  self.assertEqual({i['id'] for i in digest(self.path)['items']}, {'123', 'old'})
  self.assertEqual([i['id'] for i in result['items']], ['123'])
  self.assertEqual(result['mode'], 'live')

 def test_failure_preserves_data_and_success_time(self):
  with patch('finn.providers.announcements', return_value=[self.filing()]):
   ingest('TCS', 'announcements', self.path)
  previous = digest(self.path)['ingestion'][0]['succeeded']
  with patch('finn.providers.announcements', side_effect=OSError('offline')):
   with self.assertRaises(OSError): ingest('TCS', 'announcements', self.path)
  result = digest(self.path)
  self.assertEqual(len(result['items']), 1)
  self.assertEqual(result['ingestion'][0]['succeeded'], previous)
  self.assertTrue(result['ingestion'][0]['error'])

 def test_invalid_batch_is_atomic(self):
  with patch('finn.providers.announcements', return_value=[self.filing(), dict(self.filing('bad'), timestamp=None)]):
   with self.assertRaises(ValueError): ingest('TCS', 'announcements', self.path)
  self.assertEqual(digest(self.path)['items'], [])

 def test_price_history_upsert(self):
  data = dict(source='https://finance.yahoo.com/quote/TCS.NS', currency='INR',
              bars=[dict(as_of=self.now.isoformat(), close=100, volume=200)])
  with patch('finn.providers.prices', return_value=data):
   ingest('TCS', 'prices', self.path)
   ingest('TCS', 'prices', self.path)
  with storage(self.path) as con:
   self.assertEqual(con.execute("SELECT count(*) FROM live_items WHERE kind='prices'").fetchone()[0], 1)
  self.assertEqual(digest(self.path)['items'], [])

 def test_empty_library_has_no_demo(self):
  self.assertEqual(digest(self.path)['items'], [])

 def test_nonportfolio_filing_is_not_in_digest(self):
  with patch('finn.providers.announcements', return_value=[self.filing(symbol='OTHER')]):
   ingest('OTHER', 'announcements', self.path)
  self.assertEqual(digest(self.path)['items'], [])
  self.assertEqual(digest(self.path)['ingestion'], [])

 def test_missing_exchange_id_is_stable_across_response_order(self):
  first = self.filing(None)
  second = dict(self.filing(None), title='Different disclosure')
  with patch('finn.providers.announcements', return_value=[first, second]):
   ingest('TCS', 'announcements', self.path)
  with patch('finn.providers.announcements', return_value=[second, first]):
   ingest('TCS', 'announcements', self.path)
  self.assertEqual(len(digest(self.path)['items']), 2)
