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

Local single-user tool, no authentication or tenant separation. All uploads are visible to users of the same server. Do not upload confidential documents to a shared instance. PDF parsing is bounded by request bytes and page count, but not isolated by CPU/memory quotas. A production deployment needs sandboxed parsing, auth, per-user document scopes, provider rate limiting, structured error logging, cache eviction and a worker queue. The development HTTP server is not production-hardened.

The source URL is a citation only and is never server-fetched, avoiding arbitrary URL-fetch SSRF. Browser output is escaped; citation links allow HTTPS only. A restrictive CSP prohibits external scripts and framing. No credentials or document content are printed by application logging.

Live data and demo digest are separate. Future work is to persist validated live announcements, deduplicate exchange IDs, generate a real windowed portfolio digest and schedule EOD checks. A real investment agent additionally needs verified financial extraction and a grounded reasoning layer with explicit abstention.
