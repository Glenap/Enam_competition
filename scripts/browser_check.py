"""Run against a local server on port 8000; requires Playwright and Chromium."""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1,reduced_motion='reduce')
 errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8000',wait_until='networkidle')
 page.locator('#digest .card').first.wait_for()
 assert page.locator('#digest .card').count()==4
 page.get_by_role('button',name='3 days',exact=True).click()
 assert page.locator('#digest .card').count()==5
 assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
 (ROOT/'artifacts').mkdir(exist_ok=True)
 page.screenshot(path=str(ROOT/'artifacts/mobile-digest.png'),full_page=True,animations='disabled')
 page.get_by_role('button',name='Research',exact=True).click()
 page.locator('#research-ticker').fill('DEMO')
 page.locator('summary').filter(has_text='Add a primary source').click()
 page.locator('#doc-title').fill('SYNTHETIC browser validation transcript')
 page.locator('#doc-kind').select_option('Earnings transcript')
 page.locator('#doc-file').set_input_files(str(ROOT/'docs/synthetic-transcript.txt'))
 page.get_by_role('button',name='Add document',exact=True).click()
 page.get_by_text('Document indexed. You can now investigate it.').wait_for()
 page.locator('#question').fill('operating cash flow working capital')
 page.locator('#research-button').click()
 page.locator('#research-results blockquote').first.wait_for()
 assert 'page 2' in page.locator('#research-results').inner_text()
 page.screenshot(path=str(ROOT/'artifacts/mobile-research.png'),full_page=True,animations='disabled')
 page.get_by_role('button',name='Alert settings').click()
 page.locator('#price-threshold').fill('3.5')
 page.get_by_role('button',name='Save preferences').click()
 page.reload(wait_until='networkidle')
 page.get_by_role('button',name='Alert settings').click()
 assert page.locator('#price-threshold').input_value()=='3.5'
 page.get_by_role('button',name='Portfolio',exact=True).click()
 assert page.locator('.holding').count()==18
 page.set_viewport_size({'width':1440,'height':1000})
 page.get_by_role('button',name='Digest',exact=True).click()
 page.screenshot(path=str(ROOT/'artifacts/desktop-digest.png'),full_page=True,animations='disabled')
 assert not errors,errors
 browser.close()
 print('PASS mobile digest filtering, no overflow, upload, page-cited research, settings persistence, portfolio, desktop rendering; no JS errors')
