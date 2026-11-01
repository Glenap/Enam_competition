# Free Render demo

The user selected Render's **free** service. `render.yaml` creates a free Python web service with no disk, database, worker service or other paid resource. Automatic deployments are disabled. `FINN_DATA_DIR=/tmp/finn-data` uses temporary local SQLite storage: uploaded documents and ingestion history can disappear on restarts/redeploys. Free services can sleep when idle; polling runs only while the service is awake. This is a runnable assessment demo, not continuously available or durable hosting.

The server starts portfolio ingestion on boot, so an empty digest fills as successful source checks complete. Upload primary documents again if storage is reset. Password protection is enabled: username `finn`, password in the service's `FINN_DEMO_PASSWORD` Render environment setting. Share that secret separately with authorised reviewers. The health route is public; app assets, data and uploads require authentication. Render provides the HTTPS endpoint.

## Verification

With `FINN_DEMO_PASSWORD` configured securely, run:

```sh
.venv/bin/python -m scripts.deployment_check https://ACTUAL-SERVICE.onrender.com
```

The command checks health, authentication, assets, portfolio, live digest mode and documents. The optional `--write-probe` flag tests document writes, but survival across a hosted restart is **not guaranteed on the free plan**. Local persistence tests verify SQLite behavior only; they do not make free Render storage durable.

A free deployment can require an initial cold-start wait. Use public documents only. This remains a single-user, access-protected demo using Python's standard HTTP server; it is not a hardened multi-user product. No paid resource should be provisioned for this deployment.
