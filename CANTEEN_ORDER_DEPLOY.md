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

The customer service defaults to the public SmartCampus production URL `https://smart-campus-dashboard-kappa.vercel.app`. In the customer project's Vercel Production environment, set `CANTEEN_DASHBOARD_URL` to that exact base URL, or remove any old override so the default is used. Do not use a deployment-specific preview URL. The dashboard must provide `POST /api/canteen/orders` and accept JSON with `name` and `food`; it remains responsible for creating tokens and saving orders. This repository contains only the customer service, so deploy the dashboard separately from its own source repository and configure its database and persistent storage there.

Set `CANTEEN_ORDER_URL` on the dashboard service to the customer service's public URL if the dashboard has a link to the order page. Visitors can submit orders, but there is no customer-facing interface for editing site settings or backend configuration. Restrict deployment and environment-variable access to trusted administrators in the hosting provider.