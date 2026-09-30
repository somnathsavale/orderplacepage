import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import Flask, render_template, request

app = Flask(__name__, template_folder=".")
DASHBOARD_URL = os.environ.get(
	"CANTEEN_DASHBOARD_URL",
	"https://smart-campus-dashboard-kappa.vercel.app",
).rstrip("/")


class DashboardResponseError(Exception):
	pass


def create_dashboard_order(name, food):
	order_request = Request(
		f"{DASHBOARD_URL}/api/canteen/orders",
		data=json.dumps({"name": name, "food": food}).encode("utf-8"),
		headers={"Content-Type": "application/json"},
		method="POST",
	)
	with urlopen(order_request, timeout=10) as response:
		if response.headers.get_content_type() != "application/json":
			raise DashboardResponseError(response.headers.get_content_type())
		return json.loads(response.read().decode("utf-8"))


@app.route("/", methods=["GET", "POST"])
def order_page():
	order = None
	error = None
	queue_ahead = 0
	status_code = 200

	if request.method == "POST":
		name = request.form.get("name", "").strip()
		food = request.form.get("food", "").strip()
		if not name or not food:
			error = "Enter your name and food item to place an order."
			status_code = 400
		elif len(name) > 80 or len(food) > 120:
			error = "Keep your name under 80 characters and food item under 120."
			status_code = 400
		else:
			try:
				result = create_dashboard_order(name, food)
				order = result.get("order")
				if not result.get("ok") or not order:
					error = "The canteen could not accept this order. Please try again."
					status_code = 502
				elif order["status"] == "Waiting":
					queue_ahead = max(0, int(result.get("queue", 1)) - 1)
			except HTTPError as exc:
				app.logger.warning("Dashboard API returned HTTP %s", exc.code)
				if exc.code in (401, 403):
					error = "SmartCampus blocked this order. Check the Vercel protection bypass configuration."
				elif exc.code == 404:
					error = "SmartCampus order API was not found. Check the dashboard URL and deployment."
				else:
					error = "SmartCampus could not accept this order. Check the dashboard deployment logs."
				status_code = 502
			except URLError as exc:
				app.logger.warning("Could not reach SmartCampus: %s", exc.reason)
				error = "Cannot reach SmartCampus. Check the dashboard URL and deployment."
				status_code = 502
			except TimeoutError:
				app.logger.warning("SmartCampus order request timed out")
				error = "SmartCampus did not respond in time. Please try again shortly."
				status_code = 502
			except DashboardResponseError as exc:
				app.logger.warning("Dashboard returned non-JSON content: %s", exc)
				error = "SmartCampus returned a sign-in or error page instead of the order API response. Check its Vercel protection settings."
				status_code = 502
			except ValueError:
				app.logger.warning("Dashboard returned invalid JSON")
				error = "SmartCampus returned an invalid order response. Check the dashboard deployment logs."
				status_code = 502

	return render_template("order.html", order=order, error=error, queue_ahead=queue_ahead), status_code


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8000")), debug=False)