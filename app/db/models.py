from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    phone: Optional[str] = None
    created_at: Optional[datetime] = None


class UserCreate(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    phone: Optional[str] = None


class Product(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    discounted_price: Optional[Decimal] = None
    image_url: Optional[str] = None
    group_size_required: int = 5
    is_active: bool = True
    created_at: Optional[datetime] = None


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    discounted_price: Optional[Decimal] = None
    image_url: Optional[str] = None
    group_size_required: int = 5
    is_active: bool = True


class GroupDeal(BaseModel):
    id: int
    product_id: Optional[int] = None
    status: Literal["open", "fulfilled", "cancelled"] = "open"
    current_participants: int = 0
    created_at: Optional[datetime] = None
    fulfilled_at: Optional[datetime] = None


class GroupDealCreate(BaseModel):
    product_id: int
    status: Literal["open", "fulfilled", "cancelled"] = "open"
    current_participants: int = 0


class Coupon(BaseModel):
    id: int
    code: str
    discount_value: Decimal
    discount_type: Optional[Literal["percent", "fixed"]] = None
    valid_from: date = Field(default_factory=date.today)
    valid_to: date
    max_uses: int = 9999
    used_count: int = 0
    product_id: Optional[int] = None
    is_active: bool = True


class CouponCreate(BaseModel):
    code: str
    discount_value: Decimal
    discount_type: Literal["percent", "fixed"]
    valid_from: date = Field(default_factory=date.today)
    valid_to: date
    max_uses: int = 9999
    product_id: Optional[int] = None
    is_active: bool = True


class Order(BaseModel):
    id: int
    telegram_id: Optional[int] = None
    group_deal_id: Optional[int] = None
    coupon_id: Optional[int] = None
    phone: str
    status: Literal["pending", "confirmed", "cancelled", "refunded"] = "pending"
    total_amount: Decimal
    quantity: int = 1
    created_at: Optional[datetime] = None


class OrderCreate(BaseModel):
    telegram_id: int
    group_deal_id: int
    coupon_id: Optional[int] = None
    phone: str
    status: Literal["pending", "confirmed", "cancelled", "refunded"] = "pending"
    total_amount: Decimal
    quantity: int = 1


class CouponUsageLog(BaseModel):
    id: int
    coupon_id: Optional[int] = None
    telegram_id: Optional[int] = None
    used_at: Optional[datetime] = None


class CouponUsageLogCreate(BaseModel):
    coupon_id: int
    telegram_id: int
