"""
One-time helper to create a PayPal Product + monthly subscription Plan.

Run locally with your real PayPal REST credentials -- this is a standalone
script, not an HTTP endpoint, so it's never reachable once deployed.

Usage:
  python scripts/create_paypal_plan.py --name "Barber Monthly" --price 18 --currency USD

Reads from the environment:
  PAYPAL_CLIENT_ID       (required)
  PAYPAL_CLIENT_SECRET   (required)
  PAYPAL_MODE            "sandbox" (default) or "live"

Prints the resulting product_id and plan_id. Put plan_id into PAYPAL_PLAN_ID
and into login.vue's plan_id.
"""
import argparse
import base64
import json
import os
import urllib.request


def get_access_token(base_url, client_id, client_secret):
    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    req = urllib.request.Request(
        f"{base_url}/v1/oauth2/token",
        data=b"grant_type=client_credentials",
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())["access_token"]


def create_product(base_url, token, name):
    req = urllib.request.Request(
        f"{base_url}/v1/catalogs/products",
        data=json.dumps({"name": name, "type": "SERVICE"}).encode("utf-8"),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def create_plan(base_url, token, product_id, name, price, currency):
    body = {
        "product_id": product_id,
        "name": name,
        "billing_cycles": [{
            "frequency": {"interval_unit": "MONTH", "interval_count": 1},
            "tenure_type": "REGULAR",
            "sequence": 1,
            "total_cycles": 0,
            "pricing_scheme": {"fixed_price": {"value": str(price), "currency_code": currency}},
        }],
        "payment_preferences": {"auto_bill_outstanding": True},
    }
    req = urllib.request.Request(
        f"{base_url}/v1/billing/plans",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def main():
    parser = argparse.ArgumentParser(description="Create a PayPal Product + monthly subscription Plan.")
    parser.add_argument("--name", default="Preppy Hair Barber Subscription", help="Product/plan display name")
    parser.add_argument("--price", default="18", help="Monthly price, e.g. 18")
    parser.add_argument("--currency", default="USD", help="Currency code")
    args = parser.parse_args()

    client_id = os.environ.get("PAYPAL_CLIENT_ID")
    client_secret = os.environ.get("PAYPAL_CLIENT_SECRET")
    mode = os.environ.get("PAYPAL_MODE", "sandbox")

    if not client_id or not client_secret:
        raise SystemExit("Set PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET in your environment first.")

    base_url = "https://api-m.paypal.com" if mode == "live" else "https://api-m.sandbox.paypal.com"
    print(f"Mode: {mode} ({base_url})")

    if mode == "live":
        confirm = input("This creates a REAL product + plan on your live PayPal account. Type 'yes' to continue: ")
        if confirm.strip().lower() != "yes":
            raise SystemExit("Aborted.")

    token = get_access_token(base_url, client_id, client_secret)

    product = create_product(base_url, token, args.name)
    print(f"Product created: {product['id']}")

    plan = create_plan(
        base_url, token, product["id"],
        f"{args.name} - {args.price} {args.currency}/mo",
        args.price, args.currency,
    )
    print(f"Plan created: {plan['id']}")
    print()
    print(f"-> Set PAYPAL_PLAN_ID={plan['id']} and paste it into login.vue's plan_id.")


if __name__ == "__main__":
    main()
