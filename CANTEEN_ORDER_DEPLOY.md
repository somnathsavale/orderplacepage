# Canteen customer ordering site

`customer_app.py` is a separate customer-facing Flask site. It forwards the existing `name` and `food` form fields to the dashboard's `/api/canteen/orders` endpoint. The dashboard creates the token and stores the order in its `canteen_orders` SQLite table using the same `{token, name, food, status}` structure consumed by its canteen queue.

## Run locally

Start the dashboard with `python app.py`, then in another terminal start the customer site:

```powershell
$env:CANTEEN_DASHBOARD_URL = "http://127.0.0.1:5000"
python customer_app.py
```

Open `http://127.0.0.1:8000` for the customer form. The dashboard uses `SMART_DB` for its database path and defaults to `smart_dashboard.db` in the project directory.

## Deploy the customer service

Deploy this repository as a web service with `gunicorn --bind 0.0.0.0:$PORT customer_app:app` as its start command. The root `requirements.txt` installs Flask and Gunicorn. The customer app binds to the hosting provider's `PORT` through Gunicorn.

The customer service defaults to `https://smart-campus-dashboard-qgpvvfmoh.vercel.app` as its dashboard URL. Set `CANTEEN_DASHBOARD_URL` on the customer service if that URL changes. The dashboard must provide `POST /api/canteen/orders` and accept JSON with `name` and `food`; it remains responsible for creating tokens and saving orders. This repository contains only the customer service, so deploy the dashboard separately from its own source repository and configure its database and persistent storage there.

If the dashboard's Vercel deployment is protected, create a Protection Bypass for Automation secret in the dashboard project's Vercel settings. Add that same secret to the customer project's Production environment as `CANTEEN_DASHBOARD_BYPASS_TOKEN`, then redeploy the customer service. The customer app sends it only as the `x-vercel-protection-bypass` server-to-server header; do not commit the secret or expose it in browser code.

Set `CANTEEN_ORDER_URL` on the dashboard service to the customer service's public URL if the dashboard has a link to the order page. Visitors can submit orders, but there is no customer-facing interface for editing site settings or backend configuration. Restrict deployment and environment-variable access to trusted administrators in the hosting provider.