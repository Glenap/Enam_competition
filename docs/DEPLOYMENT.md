# Render deployment

Status: prepared and tested locally; no hosted service or deployment URL has been created. The runtime has no connected Render credential yet. Publishing this development environment does not deploy the application to Render.

The checked-in Blueprint provisions a **paid Starter web service and 1 GB persistent disk**. Review the current total shown by Render before creating resources. The former free configuration was removed because it cannot retain the SQLite database across restarts. The Blueprint passed Render's official JSON schema validation on 1 November 2026.

## Create the service

Connect the Render account securely with `RENDER_API_KEY`, or open [the Blueprint creation page](https://dashboard.render.com/select-repo?type=blueprint) and select `Glenap/Enam_competition`. Authorize GitHub access if prompted. Use `render.yaml` on `main` and inspect these settings before creating:

| Setting | Prepared value |
| --- | --- |
| Runtime | Python 3.12.8 |
| Build | `pip install -r requirements.txt` |
| Start | `python server.py --host 0.0.0.0 --port $PORT` |
| Health route | `/api/health` |
| Disk | 1 GB mounted at `/var/data/finn` |
| `FINN_DATA_DIR` | `/var/data/finn` |
| `FINN_REQUIRE_AUTH` | `1` |
| `FINN_DEMO_PASSWORD` | Generated secret, never committed |
| Automatic deploys | Off; deploy deliberately after reviewing changes |

The web server starts portfolio ingestion automatically. Keep a single service instance and do not start a duplicate standalone worker. Only files under the disk mount persist. Initial ingestion may take a few minutes; temporary source failures are recorded and retried. Persistent disks are mounted at runtime, not during the build.

After the service is live, open its actual HTTPS URL. The browser requests HTTP Basic credentials: username **finn**, password from `FINN_DEMO_PASSWORD` in the Render dashboard. Share the password separately with authorised reviewers. All app assets, data endpoints and uploads require it; the minimal health route remains public for Render. Startup fails if required authentication has no password of at least 16 characters. Use HTTPS for hosted access. Rotate the secret in the dashboard when access should be revoked.

## Verify the actual deployment

Set the same demo password in the shell through secure secret settings, then run:

```sh
.venv/bin/python -m scripts.deployment_check https://ACTUAL-SERVICE.onrender.com
.venv/bin/python -m scripts.deployment_check https://ACTUAL-SERVICE.onrender.com --write-probe
```

The second command writes an explicitly synthetic `DEMO` document and prints its ID. Restart the Render service, then use that exact ID:

```sh
.venv/bin/python -m scripts.deployment_check https://ACTUAL-SERVICE.onrender.com --expect-document DOCUMENT_ID
```

This checks health, anonymous-access rejection, authenticated routes, live digest mode and document survival after a hosted restart. The actual deployment URL and hosted persistence result must be verified before marking deployment complete or replacing the covering-note placeholder. Also open the actual URL on a physical phone, check filings/EOD source status in the digest, and upload an actual primary report for a cited research query. Live data is not shipped in Git; ingestion and public-document uploads populate the new service.

Local checks passed: 27 automated tests, including fail-closed authentication, anonymous-write rejection, malformed credentials, authorised routes, storage survival across two HTTP-server instances, and the reusable deployment checker. This does not substitute for verification on Render.

## Limits and rollback

This is an access-protected, single-user assessment demo using Python's standard HTTP server. Shared Basic credentials do not provide individual accounts, upload quotas, sandboxed PDF parsing or production resource isolation. Use public documents, limit reviewers, and disable the demo when the assessment ends. A broader launch needs a production application server and per-user authorization.

Keep disk capacity monitored and make SQLite-consistent backups. Avoid multiple workers sharing this SQLite file. A service restart with the same disk should retain data; deleting the disk or writing outside its mount will not. To roll back code, manually deploy a known-good Git commit in Render while retaining the same mounted disk, then rerun the checks. No hosting payment, service creation or environment publication has been performed by this preparation step.
