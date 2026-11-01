import datetime as dt
import hashlib
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORTFOLIO = [
 ('RELIANCE','Reliance Industries','Energy'),('TCS','Tata Consultancy Services','IT'),
 ('HDFCBANK','HDFC Bank','Banking'),('ICICIBANK','ICICI Bank','Banking'),
 ('INFY','Infosys','IT'),('BHARTIARTL','Bharti Airtel','Telecom'),
 ('ITC','ITC','Consumer'),('LT','Larsen & Toubro','Industrials'),
 ('SUNPHARMA','Sun Pharma','Healthcare'),('TATAMOTORS','Tata Motors','Auto'),
 ('TITAN','Titan','Consumer'),('ASIANPAINT','Asian Paints','Materials'),
 ('NTPC','NTPC','Utilities'),('TRENT','Trent','Retail'),
 ('DIXON','Dixon Technologies','Electronics'),('POLYCAB','Polycab India','Industrials'),
 ('CDSL','CDSL','Financial services'),('KPITTECH','KPIT Technologies','IT')]
CATEGORIES = {'Results':('financial result','quarterly result','earnings'),
 'Leadership':('resignation','appointment','managing director','cfo'),
 'M&A':('acquisition','merger','amalgamation'), 'Capital':('buyback','fund raising','preferential'),
 'Orders':('order win','contract awarded','letter of award'),
 'Routine':('trading window','newspaper','duplicate','investor meeting')}
PRIORITY = {'Results':90,'Leadership':85,'M&A':88,'Capital':75,'Orders':70,'Other':45,'Routine':10}

def ticker(value):
 value = str(value).strip().upper()
 if not re.fullmatch(r'[A-Z0-9][A-Z0-9&-]{0,29}(?:\.(?:NS|BO))?',value):
  raise ValueError('Enter an NSE symbol, or a Yahoo symbol ending in .NS or .BO.')
 return value

def classify(text):
 text = text.lower()
 return next((cat for cat,words in CATEGORIES.items() if any(w in text for w in words)), 'Other')

def alerts(closes, volumes, price_threshold=4, volume_threshold=2):
 if len(closes)<2 or len(volumes)<2: return {'change':None,'volume_ratio':None,'triggers':[]}
 prior = volumes[max(0,len(volumes)-21):-1]
 average = sum(prior)/len(prior)
 change = (closes[-1]/closes[-2]-1)*100 if closes[-2] else None
 ratio = volumes[-1]/average if average else None
 triggers=[]
 if change is not None and abs(change)>=price_threshold: triggers.append('Price threshold')
 if ratio is not None and ratio>=volume_threshold: triggers.append('Volume threshold')
 return {'change':round(change,2) if change is not None else None,
 'volume_ratio':round(ratio,2) if ratio is not None else None,'triggers':triggers}

def db(path=None):
 con=sqlite3.connect(path or ROOT/'data'/'finn.sqlite')
 con.row_factory=sqlite3.Row
 con.execute('CREATE TABLE IF NOT EXISTS documents (id TEXT PRIMARY KEY, ticker TEXT, title TEXT, kind TEXT, source TEXT, text TEXT, created TEXT)')
 return con

def add_document(symbol,title,kind,source,text,path=None):
 symbol=ticker(symbol)
 if kind not in ('Annual report','Earnings transcript','Results filing'): raise ValueError('Choose a primary document type.')
 if len(text.strip())<80: raise ValueError('Document has too little text. Scanned PDFs need OCR before upload.')
 if len(text)>1500000: raise ValueError('Document exceeds the text size limit.')
 if not title.strip(): raise ValueError('A document title is required.')
 if source and not source.startswith('https://'): raise ValueError('Source link must use HTTPS.')
 key=hashlib.sha256((symbol+text).encode()).hexdigest()[:20]
 with db(path) as con:
  con.execute('INSERT OR IGNORE INTO documents VALUES (?,?,?,?,?,?,?)',(key,symbol,title[:200],kind,source[:1000],text,dt.datetime.now(dt.timezone.utc).isoformat()))
 return key

def research(symbol,question,path=None):
 symbol=ticker(symbol)
 words=set(re.findall(r'[a-z]{3,}',question.lower()))-{'the','and','what','how','does','company','with','from'}
 with db(path) as con: docs=con.execute('SELECT * FROM documents WHERE ticker=?',(symbol,)).fetchall()
 hits=[]
 for doc in docs:
  for page_no,page in enumerate(doc['text'].split('\f'),1):
   paragraphs=[p.strip() for p in re.split(r'\n\s*\n',page) if p.strip()]
   for paragraph in paragraphs:
    for start in range(0,len(paragraph),1400):
     chunk=paragraph[start:start+1600]
     tokens=set(re.findall(r'[a-z]{3,}',chunk.lower()))
     score=len(words & tokens)
     if score:
      hits.append({'score':score,'quote':chunk,'title':doc['title'],'source':doc['source'],'page':page_no,'document_id':doc['id'],'kind':doc['kind']})
 hits.sort(key=lambda h:h['score'],reverse=True)
 selected=[]
 for hit in hits:
  if not any(hit['quote']==old['quote'] for old in selected): selected.append(hit)
  if len(selected)==5: break
 return {'ticker':symbol,'question':question,'document_count':len(docs),'evidence':selected,
 'status':'evidence' if selected else 'no_evidence',
 'method':'Extractive retrieval from uploaded primary documents. Quotes are evidence, not a generated investment conclusion.'}

def demo_feed():
 now=dt.datetime.now(dt.timezone.utc)
 fixtures=[('TCS','Results','Quarterly earnings deserve a closer look','Compare growth and margins against the preceding quarter. Open the actual filing before drawing a conclusion.',2),
 ('DIXON','Orders','A new manufacturing contract changes the watchlist','Check contract size, delivery timing and customer concentration.',4),
 ('HDFCBANK','Leadership','A leadership transition to investigate','Verify the effective date and incoming executive’s experience in the filing.',7),
 ('RELIANCE','Capital','Capital allocation is back in focus','Check the funding structure and potential dilution before interpreting the announcement.',12),
 ('TITAN','Routine','Trading-window closure','Administrative disclosure; retained in the digest for completeness.',15),
 ('INFY','Routine','Investor meeting schedule','Routine calendar update.',20),
 ('LT','M&A','A proposed acquisition enters the picture','Review consideration, approvals and strategic fit.',38)]
 return [dict(id=f'demo-{i}',ticker=s,category=c,title=t,summary=d,priority=PRIORITY[c],timestamp=(now-dt.timedelta(hours=h)).isoformat(),source=None,demo=True) for i,(s,c,t,d,h) in enumerate(fixtures)]
