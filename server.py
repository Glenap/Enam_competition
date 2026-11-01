#!/usr/bin/env python3
import argparse
import base64
import io
import json
import math
import os
import hmac
import binascii
import signal
import threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse,parse_qs
from finn.core import ROOT, PORTFOLIO, add_document, research, db
from finn.ingestion import ingest, digest, run_worker

class Handler(BaseHTTPRequestHandler):
 def send(self,status,data,ctype='application/json',headers=None):
  body=json.dumps(data).encode() if ctype=='application/json' else data
  self.send_response(status); self.send_header('Content-Type',ctype); self.send_header('Content-Length',str(len(body)))
  self.send_header('X-Content-Type-Options','nosniff'); self.send_header('Cache-Control','no-store')
  self.send_header('Content-Security-Policy',"default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'")
  for name,value in (headers or {}).items(): self.send_header(name,value)
  self.end_headers(); self.wfile.write(body)
 def authorized(self):
  password=os.environ.get('FINN_DEMO_PASSWORD','')
  required=os.environ.get('FINN_REQUIRE_AUTH')=='1'
  if not password and not required: return True
  expected=('finn:'+password).encode('utf-8')
  try:
   scheme,credential=self.headers.get('Authorization','').split(' ',1)
   supplied=base64.b64decode(credential,validate=True) if scheme.lower()=='basic' else b''
  except (ValueError,binascii.Error):
   supplied=b''
  if password and hmac.compare_digest(supplied,expected): return True
  self.send(401,{'error':'Authentication required.'},headers={'WWW-Authenticate':'Basic realm="FINN demo", charset="UTF-8"'})
  return False
 def do_GET(self):
  parsed=urlparse(self.path); q=parse_qs(parsed.query)
  if parsed.path!='/api/health' and not self.authorized(): return
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
  if not self.authorized(): return
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

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('--host',default='127.0.0.1')
 parser.add_argument('--port',type=int,default=8000)
 parser.add_argument('--poll-interval',type=int,default=900,help='Seconds between portfolio polls; 0 disables the built-in worker')
 args=parser.parse_args()
 if args.poll_interval != 0 and args.poll_interval < 900:
  parser.error('--poll-interval must be 0 or at least 900')
 if os.environ.get('FINN_REQUIRE_AUTH')=='1' and len(os.environ.get('FINN_DEMO_PASSWORD',''))<16:
  parser.error('FINN_REQUIRE_AUTH requires FINN_DEMO_PASSWORD with at least 16 characters')
 def terminate(signum,frame):
  raise KeyboardInterrupt
 signal.signal(signal.SIGTERM,terminate)
 with db(): pass
 server=ThreadingHTTPServer((args.host,args.port),Handler)
 stop=threading.Event()
 worker=None
 if args.poll_interval:
  worker=threading.Thread(target=run_worker,args=(args.poll_interval,stop),daemon=True,name='portfolio-ingestion')
  worker.start()
 print(f'FINN listening on {args.host}:{server.server_port}',flush=True)
 try:
  server.serve_forever()
 except KeyboardInterrupt:
  pass
 finally:
  stop.set()
  server.server_close()
  if worker is not None:
   worker.join(timeout=2)


if __name__=='__main__':
 main()
