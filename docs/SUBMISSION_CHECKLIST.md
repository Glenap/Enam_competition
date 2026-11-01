# Submission checklist

- [x] Local mobile-first responsive prototype files.
- [x] 18-company mock universe and arbitrary-symbol research input.
- [x] Primary-document PDF/text ingestion and page-cited retrieval.
- [x] Core tests and HTTP smoke checks.
- [x] Validate actual TCS prices and exchange disclosures (see LIVE_INGESTION.md).
- [x] Validate actual Infosys annual-report and earnings-transcript citations; record PDF hashes and evaluation manifests.
- [x] Connect digest to persistent live filings. Polling starts automatically with the server; push notifications are not implemented.
- [x] Automated Chromium checks at mobile and desktop widths; mobile screenshot visually reviewed.
- [ ] Test on a physical phone.
- [x] Deploy the user-selected free Render service and verify HTTPS, authentication, EOD prices and actual-company research.
- [ ] Resolve NSE announcement failures from Render; first hosted poll returned no filings.
- [ ] Durable hosted storage is unavailable on the chosen free plan; uploads and history may reset.
- [x] Pushed to GitHub main; implementation and deployment preparation pass 27 automated tests.
- [ ] Export/share the actual AI conversation; BUILD_HISTORY.md is only a summary.
- [ ] Replace placeholders in covering note and verify every claim.
- [ ] Send to the address in the brief, only after explicit user authorisation to send.

The supplied brief states a deadline of Sunday, 1 November 2026, without a time or timezone. The free Render deployment is live; no email submission was performed. Git publication is recorded in BUILD_HISTORY.md.
