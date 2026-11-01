"""Fixed-host, read-only public adapters; failures never become synthetic live data."""
import datetime as dt
import http.cookiejar
import json
import time
import urllib.parse
import urllib.request
from .core import ticker, classify, PRIORITY, alerts

_cache={}
def fetch(url,opener=None):
 if url in _cache and time.time()-_cache[url][0]<900: return _cache[url][1]
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'application/json','Referer':'https://www.nseindia.com/'})
 response=(opener or urllib.request.build_opener()).open(req,timeout=15)
 with response:
  raw=response.read(5000001)
 if len(raw)>5000000: raise ValueError('Source response too large')
 data=json.loads(raw)
 _cache[url]=(time.time(),data)
 return data

def prices(symbol,price_threshold=4,volume_threshold=2):
 symbol=ticker(symbol)
 yahoo=symbol if symbol.endswith(('.NS','.BO')) else symbol+'.NS'
 result=fetch('https://query1.finance.yahoo.com/v8/finance/chart/'+urllib.parse.quote(yahoo)+'?range=3mo&interval=1d')['chart']
 if result.get('error'): raise ValueError(result['error'].get('description','Price source error'))
 chart=result['result'][0]; quote=chart['indicators']['quote'][0]
 rows=[(t,c,v) for t,c,v in zip(chart['timestamp'],quote['close'],quote['volume']) if c is not None and v is not None]
 # Yahoo's final daily bar can be intraday. Exclude today until 16:00 India time.
 india=dt.timezone(dt.timedelta(hours=5,minutes=30)); now=dt.datetime.now(india)
 rows=[row for row in rows if dt.datetime.fromtimestamp(row[0],india).date()<now.date() or (dt.datetime.fromtimestamp(row[0],india).date()==now.date() and now.hour>=16)]
 if len(rows)<2: raise ValueError('Insufficient completed daily bars')
 output=alerts([r[1] for r in rows],[r[2] for r in rows],price_threshold,volume_threshold)
 return dict(output,ticker=symbol,close=rows[-1][1],as_of=dt.datetime.fromtimestamp(rows[-1][0],dt.timezone.utc).isoformat(),source='https://finance.yahoo.com/quote/'+urllib.parse.quote(yahoo),currency=chart['meta'].get('currency'),baseline_days=min(20,len(rows)-1),bars=[dict(as_of=dt.datetime.fromtimestamp(t,dt.timezone.utc).isoformat(),close=c,volume=v) for t,c,v in rows])

def announcements(symbol):
 symbol=ticker(symbol).removesuffix('.NS')
 if symbol.endswith('.BO'): raise ValueError('This filing adapter supports NSE symbols; BSE filings are not implemented.')
 opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
 with opener.open(urllib.request.Request('https://www.nseindia.com',headers={'User-Agent':'Mozilla/5.0'}),timeout=15) as response: response.read(1024)
 source_url='https://www.nseindia.com/api/corporate-announcements?index=equities&symbol='+urllib.parse.quote(symbol)
 data=fetch(source_url,opener)
 output=[]
 for item in data:
  if item.get('symbol') != symbol: continue
  title=item.get('desc','')+' — '+item.get('attchmntText','')
  cat=classify(title)
  date=item.get('an_dt','')
  try: timestamp=dt.datetime.strptime(date,'%d-%b-%Y %H:%M:%S').replace(tzinfo=dt.timezone(dt.timedelta(hours=5,minutes=30))).isoformat()
  except ValueError: timestamp=None
  output.append(dict(id=str(item['seq_id']) if item.get('seq_id') is not None else None,ticker=symbol,title=title,summary='Read the exchange filing to assess materiality.',category=cat,priority=PRIORITY[cat],timestamp=timestamp,raw_date=date,source=item.get('attchmntFile') if str(item.get('attchmntFile','')).startswith('https://') else source_url,attachment_available=str(item.get('attchmntFile','')).startswith('https://'),demo=False))
 return output
