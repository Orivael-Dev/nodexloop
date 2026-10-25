"""Small intentionally broken checkout calculation for Git-debugging exercise."""

def total_cents(items, discount_percent=0):
    """Return the final integer-cent total, with percentage discount rounded DOWN."""
    subtotal = sum(row["quantity"] * row["unit_cents"] for row in items)
    return round(subtotal * (1 - discount_percent / 100))
