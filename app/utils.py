from decimal import Decimal
from datetime import datetime, UTC
import re

from app.database import get_supabase_client


def calculate_total_amount(base_price: Decimal, quantity: int, discount: Decimal = Decimal("0")) -> Decimal:
    subtotal = base_price * quantity
    total = subtotal - discount
    if total < Decimal("0"):
        return Decimal("0")
    return total


def fetch_products() -> list[dict]:
    client = get_supabase_client()
    response = client.table("products").select("id,name,price,discounted_price,image_url,group_size_required").eq("is_active", True).execute()
    return response.data or []


def is_valid_phone_number(phone_number: str) -> bool:
    return bool(re.fullmatch(r"09\d{8}", phone_number))


def fetch_coupon_by_code(coupon_code: str) -> dict | None:
    client = get_supabase_client()
    response = (
        client.table("coupons")
        .select("id,code,used_count,max_uses,is_active")
        .eq("code", coupon_code)
        .eq("is_active", True)
        .limit(1)
        .execute()
    )
    coupons = response.data or []
    return coupons[0] if coupons else None


def ensure_user_exists(telegram_id: int, username: str | None = None, phone: str | None = None) -> None:
    client = get_supabase_client()
    payload: dict[str, object] = {"telegram_id": telegram_id}
    if username:
        payload["username"] = username
    if phone:
        payload["phone"] = phone
    client.table("users").upsert(payload, on_conflict="telegram_id").execute()

def fetch_product_by_id(product_id: int) -> dict | None:
    client = get_supabase_client()
    response = (
        client.table("products")
        .select("id,name,price,discounted_price,image_url,group_size_required")
        .eq("id", product_id)
        .eq("is_active", True)
        .limit(1)
        .execute()
    )
    products = response.data or []
    return products[0] if products else None


def confirm_order_in_db(product: dict, telegram_id: int, phone: str, coupon_code: str, username: str | None = None) -> dict:
    client = get_supabase_client()

    ensure_user_exists(telegram_id=telegram_id, username=username, phone=phone)

    product_id = int(product["id"])
    group_size_required = int(product.get("group_size_required") or 0)
    total_amount = Decimal(str(product.get("discounted_price") or product.get("price") or "0"))

    coupon_id = None
    coupon_used_count = 0
    if coupon_code.lower() not in {"none", "skip", "no", ""}:
        coupon_response = (
            client.table("coupons")
            .select("id,used_count")
            .eq("code", coupon_code)
            .eq("is_active", True)
            .limit(1)
            .execute()
        )
        coupon_data = coupon_response.data or []
        if coupon_data:
            coupon_id = coupon_data[0]["id"]
            coupon_used_count = int(coupon_data[0].get("used_count") or 0)

    group_response = (
        client.table("group_deals")
        .select("id,current_participants")
        .eq("product_id", product_id)
        .eq("status", "open")
        .order("created_at")
        .execute()
    )
    open_groups = group_response.data or []

    selected_group = None
    current_participants = 0
    for group in open_groups:
        participants = int(group.get("current_participants") or 0)
        if participants < group_size_required:
            selected_group = group
            current_participants = participants
            break

    if selected_group is None:
        created_group_response = (
            client.table("group_deals")
            .insert({"product_id": product_id, "status": "open", "current_participants": 0})
            .execute()
        )
        created_groups = created_group_response.data or []
        if not created_groups:
            raise RuntimeError("Failed to create a new group deal")
        selected_group = created_groups[0]
        current_participants = 0

    group_deal_id = int(selected_group["id"])
    order_payload = {
        "telegram_id": telegram_id,
        "group_deal_id": group_deal_id,
        "coupon_id": coupon_id,
        "phone": phone,
        "status": "pending",
        "total_amount": str(total_amount),
        "quantity": 1,
    }
    order_response = client.table("orders").insert(order_payload).execute()
    created_orders = order_response.data or []
    if not created_orders:
        raise RuntimeError("Failed to create order")

    if coupon_id is not None:
        client.table("coupons").update({"used_count": coupon_used_count + 1}).eq("id", coupon_id).execute()

    new_count = current_participants + 1
    group_updates: dict[str, object] = {"current_participants": new_count}
    if group_size_required > 0 and new_count >= group_size_required:
        group_updates["status"] = "fulfilled"
        group_updates["fulfilled_at"] = datetime.now(UTC).isoformat()

    client.table("group_deals").update(group_updates).eq("id", group_deal_id).execute()

    return {
        "order_id": created_orders[0]["id"],
        "group_deal_id": group_deal_id,
        "current_participants": new_count,
        "group_size_required": group_size_required,
    }
