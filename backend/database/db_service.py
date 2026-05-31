"""Database service for querying mock CRM customer data."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

_DATA_PATH = Path(__file__).parent / "customers.json"

with _DATA_PATH.open(encoding="utf-8") as f:
    _DATA: dict = json.load(f)

_CUSTOMERS: list[dict] = _DATA.get("customers", [])


class CustomerNotFoundError(Exception):
    """Raised when a customer ID does not exist in the CRM."""


class OrderNotFoundError(Exception):
    """Raised when an order ID does not exist for the given customer."""


def _parse_date(date_str: str) -> datetime:
    """Parse an ISO date string into a datetime object."""
    return datetime.strptime(date_str, "%Y-%m-%d")


def get_all_customers() -> list[dict]:
    """Return all customer records."""
    return _CUSTOMERS


def get_customer_by_id(customer_id: str) -> dict | None:
    """Retrieve a customer profile by ID, or None if not found."""
    for customer in _CUSTOMERS:
        if customer["customer_id"] == customer_id:
            return customer
    return None


def get_order_by_id(customer_id: str, order_id: str) -> dict | None:
    """Retrieve a specific order for a customer, or None if not found."""
    customer = get_customer_by_id(customer_id)
    if customer is None:
        return None
    for order in customer.get("orders", []):
        if order["order_id"] == order_id:
            return order
    return None


def get_customer_refund_history(customer_id: str, days: int = 60) -> list[dict]:
    """Return approved refunds for a customer within the given day window."""
    customer = get_customer_by_id(customer_id)
    if customer is None:
        raise CustomerNotFoundError(f"Customer '{customer_id}' not found")

    cutoff = datetime(2026, 5, 31) - timedelta(days=days)
    history = customer.get("refund_history", [])
    return [
        entry
        for entry in history
        if entry.get("status") == "approved"
        and _parse_date(entry["date"]) >= cutoff
    ]


def customer_exists(customer_id: str) -> bool:
    """Check whether a customer ID exists in the CRM."""
    return get_customer_by_id(customer_id) is not None
