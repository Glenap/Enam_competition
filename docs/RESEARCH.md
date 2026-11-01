# Research and implementation decisions

Research date: 1 November 2026. Source of requirements: user-supplied “ENAM_AI_Engineer_Build_Challenge_Main.pdf”, four pages. The referenced companion glossary was not supplied.

## Brief distilled

The brief prioritises a working mobile prototype and product judgment. It requests a diverse mock portfolio of 15–20 Indian listed companies, ad-hoc research beyond that portfolio, EOD prices, exchange announcements and fundamentals from annual reports/transcripts. The optional research menu includes trajectory, cash quality, guidance, and narrative-versus-numbers. Submission includes a prototype, repository, genuine AI build history and covering note.

Chosen product focus: an attention-ranked digest and an evidence-first research desk. Routine disclosures are collapsed rather than discarded. Research declines to answer when documents are absent. It generalises by symbol and uploaded document rather than hard-coding company conclusions.

## Sources consulted and access results

- Supplied challenge brief: fully extracted and read. Defines the product and required source discipline.
- https://raw.githubusercontent.com/ranaroussi/yfinance/main/README.md : fetched successfully. Describes Yahoo public APIs, single/multiple ticker access, adjustment defaults and usage terms. The current prototype directly calls Yahoo's chart endpoint rather than installing yfinance. That endpoint is unofficial and may require cookies/crumbs or change without notice.
- https://www.screener.in/company/TCS/consolidated/ : attempted; environment proxy denied CONNECT with HTTP 403. No company content retrieved.
- https://www.nseindia.com/api/corporate-announcements?index=equities&symbol=TCS : attempted; environment proxy denied CONNECT with HTTP 403. Adapter is provisional until real response validation.
- https://query1.finance.yahoo.com/v8/finance/chart/TCS.NS?range=3mo&interval=1d : attempted; environment proxy denied CONNECT with HTTP 403. No current prices retrieved.

No real company fundamentals were researched successfully. No simulated financial numbers or events are claimed as actual disclosures. Source-domain access must be enabled before validating live workflows; access alone may not overcome upstream anti-bot restrictions. Do not bypass access controls.

## Calculation choices

Daily move = (latest completed close / preceding close − 1) × 100. Volume ratio = latest volume / mean of up to 20 preceding completed sessions, excluding the latest bar. Zero denominators return missing values. Threshold comparisons are inclusive. Today’s bar is excluded before 16:00 Asia/Kolkata to avoid treating an ordinary intraday bar as EOD. Special sessions and delayed corrections are not modelled. The direct chart adapter uses unadjusted closes, so corporate actions can trigger misleading movements; adjusted-return handling is future work.

Priority is a deterministic type heuristic, not materiality analysis: results 90, M&A 88, leadership 85, capital 75, orders 70, other 45, routine 10. Future calibration should consider exposure, transaction size, novelty and source quality.

## Next useful research

Obtain two real annual reports and four earnings transcripts for one company, verify publication dates and page references, and build a manually reviewed evaluation set. Validate extraction units, consolidated versus standalone reporting, fiscal periods and management guidance before attempting automated QoQ/YoY comparisons. Confirm the current exchange symbols for the illustrative ad-hoc company chips; listings and names can change.

## Follow-up validation — 1 November 2026

The preceding access results describe the original build. Public internet now works through the approved execution path. Actual NSE TCS disclosures and Yahoo daily bars were ingested durably. Actual Infosys FY2025 annual report and Q4 FY2025 earnings transcript were downloaded from links on the issuer investor pages. Two manually selected verbatim quote/page cases passed extraction and retrieval validation. See LIVE_INGESTION.md and evaluation/infosys-results.json for precise sources, hashes, page numbering and limits. This validates citation retrieval, not financial-table extraction or investment conclusions.
