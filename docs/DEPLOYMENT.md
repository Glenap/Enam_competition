# Deployment handoff

A Render Blueprint is included in `render.yaml`. No hosting account is connected in this session, so it has not been deployed.

1. Connect the GitHub repository to your Render account and create a Blueprint from `render.yaml`.
2. The blueprint uses a free instance; its filesystem is ephemeral. Documents can disappear on restarts/redeploys. Upload public demonstration documents only. A persistent paid disk or external database is a separate decision.
3. Validate `/api/health`, all three tabs, primary document upload/retrieval, and source connectivity on the deployed service.
4. Add the verified HTTPS deployment URL to the covering note.

This configuration serves the existing single-user prototype with Python's development HTTP server. It is appropriate for a controlled assessment demonstration, not a production multi-user service. There is no login; anyone with access can read the uploaded documents. Keep it limited to public sources and shut down the demo after assessment. Before a broader launch, add a production application server, authentication, upload isolation and resource limits.

No deployment payment, hosting account or email credentials were created. Browser checks are repeatable with `python3 scripts/browser_check.py` after installing Playwright and Chromium in your development environment; these tools are not runtime dependencies.
