from decimal import Decimal


def calculate_total_amount(base_price: Decimal, quantity: int, discount: Decimal = Decimal("0")) -> Decimal:
    subtotal = base_price * quantity
    total = subtotal - discount
    if total < Decimal("0"):
        return Decimal("0")
    return total
