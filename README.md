# FINN — Your attention, invested.

A mobile-first investment intelligence prototype for the ENAM AI Engineer Build Challenge. Python 3.12, SQLite, plain HTML/CSS/JavaScript. No paid API key required.

## Run

```bash
./scripts/setup.sh
.venv/bin/python server.py --host 127.0.0.1 --port 8000
```

Open the server in your browser. The default binding is local. For a hosted demo use `--host 0.0.0.0 --port "$PORT"` behind a platform HTTPS proxy. Use a persistent disk for `data/`. This is a single-user prototype: add authentication, upload rate limits and production serving before exposing it to untrusted users.

## Try it

1. Digest: change the time window, expand routine disclosures, investigate a company. The digest reads persisted exchange filings; an empty library stays empty. Run the ingestion worker first (see below).
2. Research: choose any valid NSE symbol or `.BO` symbol. Upload an actual primary-source PDF/text document; ask a focused question and inspect verbatim, page-numbered evidence. For a deterministic demonstration, use `docs/synthetic-transcript.txt` with symbol `DEMO`. That file is fictional and clearly marked.
3. Portfolio: inspect the 18-company universe. Enter a symbol and request EOD prices or NSE filings. Failures are explicit; live failures never silently produce demo data.
4. Settings: change price/volume thresholds, saved in browser local storage and applied on the next price request.

## Verification

```bash
.venv/bin/python -m unittest discover -s tests -v
node --check web/app.js
```

Sixteen automated tests pass, including persistence, deduplication, time windows and source-failure retention. The following browser verification describes the earlier prototype: eight core tests passed. HTTP checks passed for the page, static assets, health, portfolio, digest, document ingestion and cited retrieval. PDF text extraction was verified with the supplied four-page brief. Chromium checks passed at 390px mobile and 1440px desktop widths: digest windows, upload, page-cited retrieval, saved settings and portfolio. No JavaScript errors or mobile horizontal overflow were observed. Screenshots are in `artifacts/`; repeat with `python3 scripts/browser_check.py` in a Playwright-equipped environment.

## Current boundaries

The digest now reads persistent live filing records. Manual source checks and a polling worker store filings and completed EOD bars in SQLite. Public internet access, TCS NSE filing ingestion and Yahoo EOD ingestion were verified. Research citation checks passed against Infosys’s actual FY2025 annual report and Q4 earnings transcript; manifests and PDF hashes are in `docs/evaluation/`. Research is extractive retrieval; it does not generate financial conclusions or independently verify uploaded provenance. Automatic primary-document discovery, financial comparisons and push notifications are not implemented.

```bash
python -m scripts.ingest --ticker TCS
python -m scripts.ingest --interval 900
```

Run the worker alongside the server with a shared persistent data directory. See `docs/LIVE_INGESTION.md` for operation, failure semantics, and a reproducible actual-PDF research validation command.

See `docs/RESEARCH.md`, `docs/ARCHITECTURE.md`, `docs/COVERING_NOTE.md`, `docs/SUBMISSION_CHECKLIST.md` and `docs/BUILD_HISTORY.md`.

## Deployment

Render was selected for the demo. Use `render.yaml` and `docs/DEPLOYMENT.md`. A connected hosting account is still required; no deployment URL exists yet.
