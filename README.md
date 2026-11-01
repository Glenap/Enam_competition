# FINN — Your attention, invested.

A mobile-first investment intelligence prototype for the ENAM AI Engineer Build Challenge. Python 3.12, SQLite, plain HTML/CSS/JavaScript. No paid API key required.

## Run

```bash
./scripts/setup.sh
.venv/bin/python server.py --host 127.0.0.1 --port 8000
```

Open the server in your browser. The default binding is local. For a hosted demo use `--host 0.0.0.0 --port "$PORT"` behind a platform HTTPS proxy. Use a persistent disk for `data/`. This is a single-user prototype: add authentication, upload rate limits and production serving before exposing it to untrusted users.

## Try it

1. Digest: change the time window, expand routine disclosures, investigate a company. All events are explicitly simulated and regenerated relative to the current time.
2. Research: choose any valid NSE symbol or `.BO` symbol. Upload an actual primary-source PDF/text document; ask a focused question and inspect verbatim, page-numbered evidence. For a deterministic demonstration, use `docs/synthetic-transcript.txt` with symbol `DEMO`. That file is fictional and clearly marked.
3. Portfolio: inspect the 18-company universe. Enter a symbol and request EOD prices or NSE filings. Failures are explicit; live failures never silently produce demo data.
4. Settings: change price/volume thresholds, saved in browser local storage and applied on the next price request.

## Verification

```bash
.venv/bin/python -m unittest discover -s tests -v
node --check web/app.js
```

Eight core tests passed. HTTP checks passed for the page, static assets, health, portfolio, digest, document ingestion and cited retrieval. PDF text extraction was verified with the supplied four-page brief. Chromium checks passed at 390px mobile and 1440px desktop widths: digest windows, upload, page-cited retrieval, saved settings and portfolio. No JavaScript errors or mobile horizontal overflow were observed. Screenshots are in `artifacts/`; repeat with `python3 scripts/browser_check.py` in a Playwright-equipped environment.

## Current boundaries

This is a focused local prototype, not a complete challenge submission. The digest uses simulated events. Live price and NSE adapters are implemented but not verified end-to-end: this environment rejects the source domains with HTTP 403 at its network proxy. Automatic portfolio polling, scheduled push notifications, Screener discovery, annual-report downloads, LLM synthesis, financial-table extraction and promised-versus-delivered comparisons are not implemented. Research is extractive keyword retrieval, not generative analysis. Uploads are labelled by the user; provenance is not independently verified. It does not make investment recommendations.

See `docs/RESEARCH.md`, `docs/ARCHITECTURE.md`, `docs/COVERING_NOTE.md`, `docs/SUBMISSION_CHECKLIST.md` and `docs/BUILD_HISTORY.md`.

## Deployment

Render was selected for the demo. Use `render.yaml` and `docs/DEPLOYMENT.md`. A connected hosting account is still required; no deployment URL exists yet.
