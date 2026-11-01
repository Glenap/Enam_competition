# Durable live ingestion

Run from the repository root after installing requirements:

```sh
python -m scripts.ingest --ticker TCS
python -m scripts.ingest --interval 900
```

The first command performs a targeted check; omit `--ticker` to ingest the 18-company portfolio. The second runs a foreground worker until stopped. Supervise it with your host's process manager alongside the web server, using the same persistent `data/` directory. It is not automatically deployed by render.yaml. Polls are sequential, with 15-minute source caching and a minimum 15-minute worker interval after each completed cycle. One-shot failures return a nonzero exit status; worker failures are reported and retried on the next cycle.

SQLite stores exchange filings by symbol and exchange ID (content hash fallback) and completed daily bars by symbol and timestamp. Repeated polls update records without adding duplicate rows. Batches with missing dates/citations are rejected atomically. Failed sources retain their previous records and last-success time, with an explicit failed-attempt status. These records survive process restarts when data/ is persistent. Back up the SQLite database and supply disk capacity monitoring for extended use; retention pruning is not implemented.

`/api/prices` and `/api/announcements` also persist successful fetches. `/api/digest` reads stored portfolio announcements from the last 48 hours, excludes future dates, and never fills gaps with demo data. Browser windows filter those records further. The digest shows filing links and ingestion failure status. Price records are persisted separately; they are not classified as exchange announcements. Browser thresholds apply to manual price requests; the worker uses default thresholds. No push notifications are sent.

# Real-document validation

Download actual issuer annual reports and earnings transcripts from official HTTPS sources. Create a JSON-array manifest with `ticker`, `title`, `kind`, `source`, `file`, `question`, `expected_quote`, and `expected_page`. File paths are relative to the manifest; page numbers are physical PDF pages, starting at 1. Select a short verbatim quote manually from each actual document. Include at least one Annual report and one Earnings transcript.

```sh
python -m scripts.validate_research /path/to/manifest.json
```

The command extracts real PDFs, verifies each expected quote on its specified page, indexes them into a temporary database, and requires retrieval to return that document/page/quote. Output includes original PDF SHA-256 hashes and citations. It does not independently authenticate issuer provenance or validate financial reasoning; manually check the official URL, reporting period, units and consolidated/standalone scope. No actual-company evaluation results are claimed until this command has run successfully with those documents.

# Verification in this session — 1 November 2026

Initial sandbox commands could not connect to the proxy. The approved execution path verified public internet access (GitHub HTTP 200 and Git remote access). Actual TCS ingestion then succeeded: 3,382 NSE disclosures and 64 completed Yahoo daily bars, last bar 30 October 2026. NSE returned 380 records with `-` instead of an attachment URL; these retain their exchange API citation and explicitly indicate no attachment. Symbol filtering was verified against the actual response. Some initial NSE calls failed; retained-data/error handling remains necessary.

Research validation passed against the actual Infosys FY2025 integrated annual report (369 physical PDF pages) and Q4 FY2025 earnings-call transcript (27 pages). See `evaluation/infosys-manifest.json` and `evaluation/infosys-results.json` for manually selected expected quotes, source URLs, page numbers and original PDF SHA-256 hashes. To reproduce, download the PDFs from the manifest into its directory as annual.pdf and transcript.pdf, then run the validation command with that manifest. PDFs are not committed. Annual report physical page 15 is a spread labelled printed pages 28–29; citations deliberately retain physical PDF numbering. The annual-report quote describes reported INR revenue growth, while the transcript quote gives FY2026 constant-currency guidance; these are different periods and measures and are not a promised-versus-delivered comparison.

Sixteen automated tests cover core retrieval, durable ingestion, deduplication, invalid-batch atomicity, time windows, failure retention and real-shaped NSE missing attachments. HTTP smoke tests passed for the page, JavaScript, health and live digest. JavaScript syntax and Python compilation checks passed. The worker is implemented but no hosting service or environment was republished.

Final portfolio run stored 36,397 announcements across 17 symbols and 1,088 EOD bars across 17 symbols. The remaining portfolio symbol returned no NSE disclosures. The 48-hour digest contained 25 actual disclosures when checked. CDSL's initially failed announcement request succeeded on retry. Yahoo returned HTTP 404 for TATAMOTORS; this remains an explicit failed check, without silently substituting another company/security. Portfolio tickers need ongoing maintenance after corporate actions. The local public-source research library contains both actual Infosys documents; runtime SQLite data is excluded from Git, so a fresh checkout must ingest data separately.
