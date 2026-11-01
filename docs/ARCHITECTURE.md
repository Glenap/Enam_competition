# Architecture

Browser → same-origin Python HTTP API → SQLite documents / fixed-host public adapters.

- `finn/core.py`: universe, type classification, alert calculations, deduplicated documents, page-aware extractive retrieval.
- `finn/providers.py`: Yahoo daily chart and cookie-aware NSE announcement adapter. Fifteen-minute process-local cache. Explicit upstream errors.
- `server.py`: bounded request bodies, PDF extraction, JSON routes and an allowlist of static files.
- `web/`: responsive app with digest, research, portfolio and browser-local settings.

## API

GET `/api/health`, `/api/portfolio`, `/api/digest`, `/api/documents`.
GET `/api/prices?ticker=TCS&price=4&volume=2`.
GET `/api/announcements?ticker=TCS`.
POST `/api/documents`: ticker, title, kind, source and text or base64 pdf.
POST `/api/research`: ticker and question.

Documents are content-hashed by symbol + text. PDF pages use form-feed separators; citations retain those page indices. Matching ranks unique overlapping terms and returns up to five source passages. There is no paid inference, outside model knowledge, embedding service or fabricated summary. Paragraph chunk boundaries can cut sentences; lexical matching misses semantic paraphrases.

## Operational limits

Single-user tool, no tenant separation. Optional HTTP Basic authentication protects all routes except GET /api/health when FINN_DEMO_PASSWORD is configured; FINN_REQUIRE_AUTH=1 makes hosted startup fail closed without a password of at least 16 characters. The Render Blueprint enables both and generates the password. Local startup can remain unprotected without those settings. All uploads are visible to users of the same server. Do not upload confidential documents to a shared instance. PDF parsing is bounded by request bytes and page count, but not isolated by CPU/memory quotas. A production deployment needs sandboxed parsing, individual accounts, per-user document scopes, provider rate limiting, structured error logging, cache eviction and a worker queue. The development HTTP server is not production-hardened.

The source URL is a citation only and is never server-fetched, avoiding arbitrary URL-fetch SSRF. Browser output is escaped; citation links allow HTTPS only. A restrictive CSP prohibits external scripts and framing. No credentials or document content are printed by application logging.

The digest now reads durable portfolio announcements from SQLite, with exchange-ID deduplication, timestamp validation and failed-attempt tracking. `finn/ingestion.py` persists completed price bars separately. The server starts an immediate polling worker by default with a 900-second interval after each cycle; `--poll-interval 0` disables it. `python -m scripts.ingest --interval 900` remains an alternative foreground worker. `FINN_DATA_DIR` selects persistent storage; Manual source endpoints also persist their responses. The digest serves seven days for the UI’s three windows and excludes retired/ad-hoc symbols from portfolio status. See LIVE_INGESTION.md. Actual TCS NSE and Yahoo responses were verified in this session; see LIVE_INGESTION.md for results and remaining limits. A real investment agent additionally needs verified financial extraction and a grounded reasoning layer with explicit abstention.
