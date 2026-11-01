"""Check a hosted FINN demo. Password comes only from FINN_DEMO_PASSWORD.

python -m scripts.deployment_check https://your-service.onrender.com
Add --write-probe, restart the service, then use --expect-document ID to check disk persistence.
"""
import argparse
import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request


def check(base, allow_http=False, write_probe=False, expect_document=None):
 parsed=urllib.parse.urlparse(base)
 if parsed.scheme not in (('https','http') if allow_http else ('https',)) or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ('','/'):
  raise ValueError('Use an HTTPS origin without credentials, path, query or fragment')
 password=os.environ.get('FINN_DEMO_PASSWORD','')
 if not password: raise ValueError('Set FINN_DEMO_PASSWORD securely before validation')
 base=base.rstrip('/')
 def request(path,authenticated=False,body=None):
  headers={}
  if authenticated: headers['Authorization']='Basic '+base64.b64encode(('finn:'+password).encode()).decode()
  if body is not None: headers['Content-Type']='application/json'
  req=urllib.request.Request(base+path,data=json.dumps(body).encode() if body is not None else None,headers=headers)
  try:
   with urllib.request.urlopen(req,timeout=30) as response:
    return response.status,response.read(),response.headers
  except urllib.error.HTTPError as error:
   return error.code,error.read(),error.headers
 status,body,_=request('/api/health')
 if status!=200 or json.loads(body).get('status')!='ok': raise ValueError('Health check failed')
 for route in ('/','/api/documents','/api/digest'):
  status,_,headers=request(route)
  if status!=401 or 'Basic' not in headers.get('WWW-Authenticate',''): raise ValueError('Authentication gate failed: '+route)
 for route in ('/','/app.js','/api/portfolio','/api/digest','/api/documents'):
  status,body,_=request(route,True)
  if status!=200: raise ValueError('Authenticated route failed: '+route)
  if route=='/api/digest' and json.loads(body).get('mode')!='live': raise ValueError('Digest is not live')
 result={'status':'passed','origin':base,'checks':['health','authentication','page','assets','portfolio','live digest','documents']}
 if write_probe:
  status,body,_=request('/api/documents',True,dict(ticker='DEMO',title='SYNTHETIC deployment persistence probe',kind='Results filing',source='',text='SYNTHETIC deployment storage check. This document contains no actual company facts or investment conclusions.'))
  if status!=201: raise ValueError('Persistence probe upload failed')
  result['probe_document_id']=json.loads(body)['id']
  expect_document=result['probe_document_id']
 if expect_document:
  status,body,_=request('/api/documents',True)
  if status!=200 or not any(doc['id']==expect_document for doc in json.loads(body)):
   raise ValueError('Expected document not found on persistent storage')
  result['document_found']=expect_document
 return result


if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('origin')
 parser.add_argument('--allow-http',action='store_true',help='Local validation only; hosted services must use HTTPS')
 parser.add_argument('--write-probe',action='store_true')
 parser.add_argument('--expect-document')
 args=parser.parse_args()
 print(json.dumps(check(args.origin,args.allow_http,args.write_probe,args.expect_document),indent=2))
