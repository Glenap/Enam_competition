"""Validate page-cited retrieval against locally downloaded primary-source PDFs.

Run: python -m scripts.validate_research manifest.json
Manifest is a JSON array: ticker, title, kind, source (official HTTPS URL), file,
question, expected_quote and expected_page. Paths are relative to the manifest.
Use at least one annual report and one earnings transcript. This checks extraction
and retrieval, not issuer authenticity or the correctness of financial claims.
"""
import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from urllib.parse import urlparse
from finn.core import add_document, research


def validate(manifest):
 from pypdf import PdfReader
 manifest = Path(manifest)
 entries = json.loads(manifest.read_text())
 if not {'Annual report', 'Earnings transcript'} <= {entry['kind'] for entry in entries}:
  raise ValueError('Supply actual annual-report and earnings-transcript cases')
 results = []
 with tempfile.TemporaryDirectory() as temp:
  database = Path(temp) / 'validation.sqlite'
  for entry in entries:
   source = urlparse(entry['source'])
   if source.scheme != 'https' or not source.hostname:
    raise ValueError('An official HTTPS source URL is required')
   raw = (manifest.parent / entry['file']).read_bytes()
   import io
   reader = PdfReader(io.BytesIO(raw))
   pages = [page.extract_text() or '' for page in reader.pages]
   page = entry['expected_page']
   quote = entry['expected_quote']
   if not quote.strip() or not 1 <= page <= len(pages) or quote not in pages[page-1]:
    raise ValueError('Expected verbatim quote does not occur on the specified PDF page')
   key = add_document(entry['ticker'], entry['title'], entry['kind'], entry['source'], '\f'.join(pages), database)
   evidence = research(entry['ticker'], entry['question'], database)['evidence']
   if not any(hit['document_id'] == key and hit['page'] == page and quote in hit['quote'] for hit in evidence):
    raise ValueError('Retrieval did not return the expected document, page and quote')
   results.append(dict(title=entry['title'], source=entry['source'], sha256=hashlib.sha256(raw).hexdigest(),
                       page=page, quote=quote, status='passed'))
 return results


if __name__ == '__main__':
 parser = argparse.ArgumentParser(description=__doc__)
 parser.add_argument('manifest')
 args = parser.parse_args()
 print(json.dumps(validate(args.manifest), indent=2))
