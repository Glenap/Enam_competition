import unittest
from unittest.mock import patch, MagicMock
from finn.providers import announcements


class AnnouncementTests(unittest.TestCase):
 def test_real_shape_missing_attachment_and_symbol_filter(self):
  rows=[dict(symbol='TCS',seq_id='42',an_dt='19-Oct-2026 11:30:07',desc='News Verification',attchmntFile='-'),
        dict(symbol='OTHER',seq_id='43',an_dt='19-Oct-2026 11:30:07',desc='Other filing',attchmntFile='https://example.com/report.pdf')]
  with patch('finn.providers.urllib.request.build_opener',return_value=MagicMock()), patch('finn.providers.fetch',return_value=rows):
   result=announcements('TCS.NS')
  self.assertEqual(len(result),1)
  self.assertEqual(result[0]['id'],'42')
  self.assertEqual(result[0]['timestamp'],'2026-10-19T11:30:07+05:30')
  self.assertFalse(result[0]['attachment_available'])
  self.assertEqual(result[0]['source'],'https://www.nseindia.com/api/corporate-announcements?index=equities&symbol=TCS')
