import tempfile
import unittest
from pathlib import Path
from finn.core import alerts, classify, add_document, research, ticker, demo_feed, PORTFOLIO
class CoreTests(unittest.TestCase):
 def test_volume_baseline_excludes_current(self):
  r=alerts([100]*20+[105],[100]*20+[250]); self.assertEqual(r['volume_ratio'],2.5); self.assertEqual(len(r['triggers']),2)
 def test_zero_baseline(self):
  r=alerts([0,1],[0,1]); self.assertIsNone(r['change']); self.assertIsNone(r['volume_ratio'])
 def test_negative_price_alert(self): self.assertIn('Price threshold',alerts([100,90],[100,100])['triggers'])
 def test_symbols(self):
  self.assertEqual(ticker('m&m.ns'),'M&M.NS')
  with self.assertRaises(ValueError): ticker('../etc/passwd')
 def test_routine(self):
  self.assertEqual(classify('Closure of trading window'),'Routine')
  self.assertEqual(classify('Newspaper publication of financial results'),'Routine')
 def test_retrieval_and_isolation(self):
  with tempfile.TemporaryDirectory() as temp:
   path=Path(temp)/'test.sqlite'
   text='First page with company description and business segments. '*3+'\fRevenue growth guidance is 12 percent for the next financial year. Margin guidance is stable.'
   key=add_document('TEST','Synthetic test transcript','Earnings transcript','https://example.com/report',text,path)
   self.assertEqual(key,add_document('TEST','Duplicate','Earnings transcript','',text,path))
   result=research('TEST','revenue growth guidance',path)
   self.assertEqual(result['document_count'],1); self.assertEqual(result['evidence'][0]['page'],2)
   self.assertEqual(research('OTHER','growth',path)['status'],'no_evidence')
   self.assertEqual(research('TEST','unmatchedword',path)['status'],'no_evidence')
 def test_primary_document_type(self):
  with self.assertRaises(ValueError): add_document('TEST','News','Broker note','','x'*100)
 def test_demo_honesty(self):
  self.assertEqual(len(PORTFOLIO),18)
  self.assertTrue(all(e['demo'] and e['source'] is None for e in demo_feed()))
if __name__=='__main__': unittest.main()
