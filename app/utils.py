from decimal import Decimal

from app.database import get_supabase_client


def calculate_total_amount(base_price: Decimal, quantity: int, discount: Decimal = Decimal("0")) -> Decimal:
    subtotal = base_price * quantity
    total = subtotal - discount
    if total < Decimal("0"):
        return Decimal("0")
    return total


def fetch_products() -> list[dict]:
    client = get_supabase_client()
    response = client.table("products").select("id,name,price,image_url").eq("is_active", True).execute()
    return response.data or []
