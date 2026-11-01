import base64
import contextlib
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from server import Handler
from scripts.deployment_check import check


class QuietHandler(Handler):
 def log_message(self,*args): pass


@contextlib.contextmanager
def serving():
 server=ThreadingHTTPServer(('127.0.0.1',0),QuietHandler)
 thread=threading.Thread(target=server.serve_forever,daemon=True)
 thread.start()
 try: yield f'http://127.0.0.1:{server.server_port}'
 finally:
  server.shutdown()
  server.server_close()
  thread.join()


class DeploymentTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory()
  self.addCleanup(self.temp.cleanup)
  self.environment=patch.dict(os.environ,{'FINN_DATA_DIR':self.temp.name,'FINN_REQUIRE_AUTH':'1','FINN_DEMO_PASSWORD':'test-only-secret-password'})
  self.environment.start()
  self.addCleanup(self.environment.stop)

 def request(self,base,path,credential=None,body=None):
  headers={}
  if credential: headers['Authorization']=credential
  req=urllib.request.Request(base+path,data=body,headers=headers)
  try:
   with urllib.request.urlopen(req) as response:return response.status,response.read(),response.headers
  except urllib.error.HTTPError as error:return error.code,error.read(),error.headers

 def test_all_data_and_writes_require_authentication(self):
  with serving() as base:
   for route in ('/','/app.js','/api/documents','/api/portfolio','/api/digest','/api/prices?ticker=TCS'):
    status,_,headers=self.request(base,route)
    self.assertEqual(status,401)
    self.assertIn('Basic',headers['WWW-Authenticate'])
   self.assertEqual(self.request(base,'/api/documents',body=b'{}')[0],401)
   self.assertFalse((Path(self.temp.name)/'finn.sqlite').exists())
   self.assertEqual(self.request(base,'/api/health')[0],200)
   self.assertEqual(self.request(base,'/api/health',body=b'{}')[0],401)

 def test_wrong_and_malformed_credentials_are_rejected(self):
  with serving() as base:
   for credential in ('Basic !!!','Bearer nope','Basic '+base64.b64encode(b'finn:wrong').decode()):
    self.assertEqual(self.request(base,'/',credential)[0],401)

 def test_required_auth_fails_closed_without_password(self):
  with patch.dict(os.environ,{'FINN_DEMO_PASSWORD':''}),serving() as base:
   self.assertEqual(self.request(base,'/')[0],401)

 def test_smoke_probe_survives_server_restart(self):
  with serving() as base:
   result=check(base,allow_http=True,write_probe=True)
   key=result['probe_document_id']
  with serving() as base:
   result=check(base,allow_http=True,expect_document=key)
   self.assertEqual(result['document_found'],key)
   with self.assertRaisesRegex(ValueError,'HTTPS'):check(base)

 def test_local_mode_can_remain_unprotected(self):
  with patch.dict(os.environ,{'FINN_REQUIRE_AUTH':'','FINN_DEMO_PASSWORD':''}),serving() as base:
   self.assertEqual(self.request(base,'/')[0],200)

 def test_hosted_startup_refuses_missing_password(self):
  with patch.dict(os.environ,{'FINN_DEMO_PASSWORD':''}):
   result=subprocess.run([sys.executable,'server.py','--poll-interval','0'],capture_output=True,text=True)
  self.assertEqual(result.returncode,2)
  self.assertIn('at least 16 characters',result.stderr)
