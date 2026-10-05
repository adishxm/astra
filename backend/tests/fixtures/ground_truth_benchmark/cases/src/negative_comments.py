"""Module for calculating order totals."""

# Historical note: We previously used DES and SHA1 in 2005.
# RSA 1024 was deprecated long ago.

def calculate_total(items: list) -> float:
    """Sum item prices."""
    total = 0.0
    for item in items:
        total += item.get('price', 0.0)
    return total
