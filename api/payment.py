from http.server import BaseHTTPRequestHandler
import json
import os
import base64
import urllib.request
import urllib.error

# PayPal REST API credentials (set these in Vercel project env vars)
PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.environ.get("PAYPAL_CLIENT_SECRET")
PAYPAL_MODE = os.environ.get("PAYPAL_MODE", "sandbox")  # "sandbox" or "live"
# The Plan ID for the $3/month subscription, created once via PayPal
# (dashboard or /v1/billing/plans). Used to make sure the subscription
# a client sends us is actually the plan we expect, not some other one.
PAYPAL_PLAN_ID = os.environ.get("PAYPAL_PLAN_ID")

PAYPAL_BASE_URL = (
    "https://api-m.paypal.com" if PAYPAL_MODE == "live" else "https://api-m.sandbox.paypal.com"
)

# Supabase service-role credentials, for privileged writes (e.g. creating a
# barber record right after signup, before the user has confirmed their
# email / has an active session, when RLS would otherwise block the insert).
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.environ.get("SUPABASE_SECRET_KEY")
# Lower-privilege key, used only to ask Supabase "who does this access token
# belong to" -- never used for writes.
SUPABASE_PUBLISHABLE_KEY = os.environ.get("SUPABASE_PUBLISHABLE_KEY")


def get_paypal_access_token():
    """OAuth2 client-credentials grant, needed before any other PayPal API call."""
    auth = base64.b64encode(f"{PAYPAL_CLIENT_ID}:{PAYPAL_CLIENT_SECRET}".encode()).decode()
    req = urllib.request.Request(
        f"{PAYPAL_BASE_URL}/v1/oauth2/token",
        data=b"grant_type=client_credentials",
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())["access_token"]


def get_paypal_subscription(subscription_id, access_token):
    req = urllib.request.Request(
        f"{PAYPAL_BASE_URL}/v1/billing/subscriptions/{subscription_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        method="GET",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def create_paypal_product(access_token):
    req = urllib.request.Request(
        f"{PAYPAL_BASE_URL}/v1/catalogs/products",
        data=json.dumps({
            "name": "Preppy Hair Barber Subscription",
            "type": "SERVICE",
        }).encode('utf-8'),
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def create_paypal_plan(access_token, product_id):
    req = urllib.request.Request(
        f"{PAYPAL_BASE_URL}/v1/billing/plans",
        data=json.dumps({
            "product_id": product_id,
            "name": "Barber Monthly - 3 USD",
            "billing_cycles": [{
                "frequency": {"interval_unit": "MONTH", "interval_count": 1},
                "tenure_type": "REGULAR",
                "sequence": 1,
                "total_cycles": 0,
                "pricing_scheme": {"fixed_price": {"value": "3", "currency_code": "USD"}},
            }],
            "payment_preferences": {"auto_bill_outstanding": True},
        }).encode('utf-8'),
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def create_barber_record(barber_id, barber_name):
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/preppyhair_barbers",
        data=json.dumps({
            "barber_id": barber_id,
            "barber_name": barber_name,
        }).encode('utf-8'),
        headers={
            "apikey": SUPABASE_SECRET_KEY,
            "Authorization": f"Bearer {SUPABASE_SECRET_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def get_supabase_user_from_token(access_token):
    """Resolve who an access token belongs to. Never trust a client-supplied
    user id for a destructive action -- always derive it from their token."""
    req = urllib.request.Request(
        f"{SUPABASE_URL}/auth/v1/user",
        headers={
            "apikey": SUPABASE_PUBLISHABLE_KEY,
            "Authorization": f"Bearer {access_token}",
        },
        method="GET",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def cancel_paypal_subscription(subscription_id, access_token):
    req = urllib.request.Request(
        f"{PAYPAL_BASE_URL}/v1/billing/subscriptions/{subscription_id}/cancel",
        data=json.dumps({"reason": "Account deleted by user"}).encode('utf-8'),
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    urllib.request.urlopen(req)  # 204 No Content on success


def delete_barber_record(barber_id):
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/preppyhair_barbers?barber_id=eq.{barber_id}",
        headers={
            "apikey": SUPABASE_SECRET_KEY,
            "Authorization": f"Bearer {SUPABASE_SECRET_KEY}",
        },
        method="DELETE",
    )
    urllib.request.urlopen(req)


def delete_barber_table_rows(table, barber_id):
    """Delete every row in `table` keyed to this barber_id. Needed before
    delete_supabase_user, since walkins/appointments hold a foreign key to
    auth.users(id) and Postgres refuses to delete a still-referenced user."""
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/{table}?barber_id=eq.{barber_id}",
        headers={
            "apikey": SUPABASE_SECRET_KEY,
            "Authorization": f"Bearer {SUPABASE_SECRET_KEY}",
        },
        method="DELETE",
    )
    urllib.request.urlopen(req)


def delete_supabase_user(user_id):
    req = urllib.request.Request(
        f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}",
        headers={
            "apikey": SUPABASE_SECRET_KEY,
            "Authorization": f"Bearer {SUPABASE_SECRET_KEY}",
        },
        method="DELETE",
    )
    urllib.request.urlopen(req)


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. Read the length of the data and parse the JSON body
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        body = json.loads(post_data.decode('utf-8'))

        # 2. Extract values from frontend form
        notify_type = body.get("notify_type")

        try:
            if notify_type == "paypal-pay":
                # Frontend calls this right after PayPal's onApprove callback,
                # passing the subscriptionID it just got back from PayPal.
                subscription_id = body.get("subscription_id")

                if not subscription_id:
                    raise ValueError("Missing subscription_id")

                access_token = get_paypal_access_token()
                subscription = get_paypal_subscription(subscription_id, access_token)

                is_active = subscription.get("status") == "ACTIVE"
                is_expected_plan = (
                    PAYPAL_PLAN_ID is None or subscription.get("plan_id") == PAYPAL_PLAN_ID
                )

                if not (is_active and is_expected_plan):
                    self.send_response(402)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    error_data = {
                        "success": False,
                        "error": "Subscription is not active.",
                        "status": subscription.get("status"),
                    }
                    self.wfile.write(json.dumps(error_data).encode('utf-8'))
                    return

                # TODO: once we decide where subscriptions live, persist
                # subscription_id / status against the barber/user record here.

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response_data = {
                    "success": True,
                    "status": subscription.get("status"),
                    "subscription_id": subscription_id,
                }
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
            elif notify_type == "paypal-setup-plan":
                # One-time dev helper: creates a Product + $3/month Plan and
                # hands back the Plan ID. Only runs in sandbox mode so this
                # endpoint can never spin up a real billing plan by accident.
                if PAYPAL_MODE == "live":
                    self.send_response(403)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    error_data = {"success": False, "error": "Refusing to run plan setup in live mode."}
                    self.wfile.write(json.dumps(error_data).encode('utf-8'))
                    return

                access_token = get_paypal_access_token()
                product = create_paypal_product(access_token)
                plan = create_paypal_plan(access_token, product["id"])

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response_data = {
                    "success": True,
                    "product_id": product.get("id"),
                    "plan_id": plan.get("id"),
                }
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
            elif notify_type == "register-barber":
                # Frontend calls this right after supabase.auth.signUp()
                # succeeds, once it has the new user's id. Uses the Supabase
                # service-role key so the insert works even before the user
                # has confirmed their email / has a session (RLS would
                # otherwise block a self-serve insert at that point).
                barber_id = body.get("barber_id")
                barber_name = body.get("barber_name")

                if not barber_id or not barber_name:
                    raise ValueError("Missing barber_id or barber_name")

                create_barber_record(barber_id, barber_name)

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode('utf-8'))
            elif notify_type == "delete-account":
                # Frontend calls this with the caller's own Supabase access
                # token in the Authorization header. We resolve the user id
                # from that token server-side rather than trusting anything
                # in the request body -- this action is irreversible, so it
                # must not be possible to delete someone else's account.
                auth_header = self.headers.get('Authorization', '')
                access_token = auth_header.replace('Bearer ', '').strip()

                if not access_token:
                    raise ValueError("Missing Authorization header")

                supabase_user = get_supabase_user_from_token(access_token)
                user_id = supabase_user.get("id")

                if not user_id:
                    raise ValueError("Could not verify user from access token")

                subscription_id = (supabase_user.get("user_metadata") or {}).get("paypal_subscription_id")

                if subscription_id:
                    try:
                        paypal_token = get_paypal_access_token()
                        cancel_paypal_subscription(subscription_id, paypal_token)
                    except urllib.error.HTTPError as e:
                        # Already cancelled/expired subscriptions 422 here --
                        # don't let that block the account deletion itself.
                        print(f"PayPal cancel warning for {subscription_id}: {e.read().decode()}")

                for table in ("walkins", "appointments"):
                    try:
                        delete_barber_table_rows(table, user_id)
                    except urllib.error.HTTPError as e:
                        print(f"{table} delete warning for {user_id}: {e.read().decode()}")

                try:
                    delete_barber_record(user_id)
                except urllib.error.HTTPError as e:
                    print(f"Barber record delete warning for {user_id}: {e.read().decode()}")

                delete_supabase_user(user_id)

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode('utf-8'))
            else:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "Unknown notify_type"}).encode('utf-8'))

        except urllib.error.HTTPError as e:
            # PayPal returned a non-2xx (e.g. bad/expired subscription_id)
            self.send_response(502)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_data = {"success": False, "error": f"PayPal API error: {e.read().decode()}"}
            self.wfile.write(json.dumps(error_data).encode('utf-8'))
        except Exception as e:
            # Handle backend errors safely
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            error_data = {"success": False, "error": str(e)}
            self.wfile.write(json.dumps(error_data).encode('utf-8'))
