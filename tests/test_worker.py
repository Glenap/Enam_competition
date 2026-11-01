import os
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from finn.core import db, PORTFOLIO
from finn.ingestion import poll, run_worker
from finn.providers import prices, announcements


class WorkerTests(unittest.TestCase):
 def test_stop_prevents_any_source_requests(self):
  stop = threading.Event()
  stop.set()
  with patch('finn.ingestion.ingest') as ingest:
   self.assertEqual(poll(['TCS'], stop_event=stop), [])
   ingest.assert_not_called()

 def test_poll_failure_does_not_stop_other_sources(self):
  with patch('finn.ingestion.ingest', side_effect=[OSError('offline'), {}, [], {}]) as ingest:
   self.assertEqual(poll(['TCS', 'INFY']), [{'ticker':'TCS','kind':'announcements'}])
   self.assertEqual(ingest.call_count, 4)

 def test_worker_polls_immediately_then_waits_interruptibly(self):
  stop = MagicMock()
  stop.is_set.return_value = False
  stop.wait.return_value = True
  with patch('finn.ingestion.poll', return_value=[]) as poll_once, patch('builtins.print'):
   run_worker(900, stop, ['TMPV'])
  poll_once.assert_called_once_with(['TMPV'], None, stop)
  stop.wait.assert_called_once_with(900)
  with self.assertRaises(ValueError): run_worker(1, stop)

 def test_data_directory_can_be_mounted_independently(self):
  with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {'FINN_DATA_DIR':temp}):
   with db() as con: con.execute("INSERT INTO documents VALUES ('test','TCS','Title','Annual report','','text','now')")
   with db() as con: self.assertEqual(con.execute('SELECT count(*) FROM documents').fetchone()[0], 1)
   self.assertTrue((Path(temp)/'finn.sqlite').exists())

 def test_legacy_symbol_explains_successors_without_fetching(self):
  with patch('finn.providers.fetch') as fetch:
   for provider in (prices, announcements):
    with self.assertRaisesRegex(ValueError,'TMPV.*TMCV'):
     provider('TATAMOTORS.NS')
   fetch.assert_not_called()
  self.assertIn('TMPV', {row[0] for row in PORTFOLIO})
  self.assertNotIn('TATAMOTORS', {row[0] for row in PORTFOLIO})
