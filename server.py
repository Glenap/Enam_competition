#!/usr/bin/env python3
import argparse
import base64
import io
import json
import math
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse,parse_qs
from finn.core import ROOT, PORTFOLIO, add_document, research, db
from finn.ingestion import ingest, digest

class Handler(BaseHTTPRequestHandler):
 def send(self,status,data,ctype='application/json'):
  body=json.dumps(data).encode() if ctype=='application/json' else data
  self.send_response(status); self.send_header('Content-Type',ctype); self.send_header('Content-Length',str(len(body)))
  self.send_header('X-Content-Type-Options','nosniff'); self.send_header('Cache-Control','no-store')
  self.send_header('Content-Security-Policy',"default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'")
  self.end_headers(); self.wfile.write(body)
 def do_GET(self):
  parsed=urlparse(self.path); q=parse_qs(parsed.query)
  try:
   if parsed.path=='/api/health': return self.send(200,{'status':'ok'})
   if parsed.path=='/api/portfolio': return self.send(200,[dict(ticker=s,name=n,sector=c) for s,n,c in PORTFOLIO])
   if parsed.path=='/api/digest': return self.send(200,digest())
   if parsed.path=='/api/documents':
    with db() as con: data=[dict(r) for r in con.execute('SELECT id,ticker,title,kind,source,created FROM documents ORDER BY created DESC')]
    return self.send(200,data)
   if parsed.path in ('/api/prices','/api/announcements'):
    symbol=q.get('ticker',[''])[0]
    if parsed.path.endswith('prices'):
     p=float(q.get('price',['4'])[0]); v=float(q.get('volume',['2'])[0])
     if not math.isfinite(p) or not math.isfinite(v) or not 0<p<=100 or not 0<v<=100: raise ValueError('Thresholds must be between 0 and 100.')
     data=ingest(symbol,'prices',price=p,volume=v)
    else: data=ingest(symbol,'announcements')
    return self.send(200,data)
   paths={'/':'index.html','/app.js':'app.js','/style.css':'style.css'}
   if parsed.path not in paths: return self.send(404,{'error':'Not found'})
   file=ROOT/'web'/paths[parsed.path]
   return self.send(200,file.read_bytes(),{'.html':'text/html; charset=utf-8','.js':'application/javascript','.css':'text/css'}[file.suffix])
  except ValueError as e: self.send(400,{'error':str(e)})
  except Exception: self.send(502,{'error':'Public source unavailable or returned an unsupported response. Previously stored records are retained; retry later or upload primary documents.'})
 def do_POST(self):
  try:
   size=int(self.headers.get('Content-Length','0'))
   if not 0<size<=12000000: return self.send(413,{'error':'Request must be between 1 byte and 12 MB.'})
   data=json.loads(self.rfile.read(size))
   if self.path=='/api/research': return self.send(200,research(data.get('ticker',''),str(data.get('question',''))[:1000]))
   if self.path=='/api/documents':
    text=data.get('text','')
    if data.get('pdf'):
     from pypdf import PdfReader
     raw=base64.b64decode(data['pdf'],validate=True)
     reader=PdfReader(io.BytesIO(raw))
     if len(reader.pages)>600: raise ValueError('PDF exceeds 600 pages.')
     text='\f'.join(page.extract_text() or '' for page in reader.pages)
    key=add_document(data.get('ticker',''),data.get('title',''),data.get('kind',''),data.get('source',''),text)
    return self.send(201,{'id':key})
   self.send(404,{'error':'Not found'})
  except (ValueError,TypeError,KeyError) as e: self.send(400,{'error':str(e)})
  except Exception: self.send(400,{'error':'Could not read this document. Try a text-based PDF or a UTF-8 text file.'})

if __name__=='__main__':
 parser=argparse.ArgumentParser(); parser.add_argument('--host',default='127.0.0.1'); parser.add_argument('--port',type=int,default=8000); args=parser.parse_args()
 (ROOT/'data').mkdir(exist_ok=True)
 with db(): pass
 print(f'FINN listening on {args.host}:{args.port}',flush=True)
 ThreadingHTTPServer((args.host,args.port),Handler).serve_forever()
