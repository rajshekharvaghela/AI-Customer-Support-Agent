"""Policy service for loading and summarizing refund policy documents."""

from pathlib import Path

_POLICY_PATH = Path(__file__).parent / "refund_policy.txt"


def get_refund_policy() -> str:
    """Load and return the full refund policy document text."""
    if not _POLICY_PATH.exists():
        raise FileNotFoundError(f"Policy file not found at {_POLICY_PATH}")
    return _POLICY_PATH.read_text(encoding="utf-8")


def get_policy_summary() -> str:
    """Return a shortened version of the policy for system prompts."""
    return """
WORKNOON REFUND POLICY SUMMARY:
1. Standard return window: 30 days from delivery. Electronics: 14 days.
2. Final sale items: NEVER eligible for refund.
3. Clearance items: NOT eligible for refund.
4. Custom/personalized/engraved items: NOT eligible for refund.
5. Item must be unopened. Opened items: DENY.
6. Damaged (customer fault): DENY. Damaged (shipping fault): APPROVE if compliant.
7. Under $100: auto-approve if compliant.
8. $100–$500: approve after validation.
9. Over $500: ESCALATE — agent must not approve or deny.
10. Processing orders: cannot refund — must cancel instead.
11. Cancelled orders: not eligible for refund.
12. More than 2 refunds in 60 days: ESCALATE to human supervisor.
""".strip()
