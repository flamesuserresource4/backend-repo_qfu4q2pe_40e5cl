"""
Database Schemas for Art Marketplace & Community

Each Pydantic model below maps to a MongoDB collection (lowercased class name).
These schemas are used for validation and by the built-in database viewer.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Literal
from datetime import datetime

# ---------------------------------------------------------------------------
# Accounts
# ---------------------------------------------------------------------------
class User(BaseModel):
    name: str = Field(..., description="Display name")
    email: str = Field(..., description="Email address")
    role: Literal["artist", "collector", "both"] = "both"
    avatar_url: Optional[HttpUrl] = None
    bio: Optional[str] = ""
    location: Optional[str] = None
    is_active: bool = True

# ---------------------------------------------------------------------------
# Art Showcase (not traditional e-commerce SKU)
# ---------------------------------------------------------------------------
class Artwork(BaseModel):
    artist_id: str = Field(..., description="Creator's user id")
    title: str
    story: Optional[str] = Field(
        None,
        description="Narrative/context. Buyers decide beyond just an image."
    )
    media: Optional[str] = Field(None, description="e.g., Oil on canvas")
    dimensions: Optional[str] = Field(None, description="e.g., 24x36 in")
    year: Optional[int] = None
    images: List[HttpUrl] = []
    price_range: Optional[str] = Field(
        None, description="e.g., 1,000–1,500 USD (range instead of fixed price)"
    )
    availability_status: Literal["available", "reserved", "sold", "commission_only"] = "available"
    tags: List[str] = []
    location: Optional[str] = None
    shipping_options: List[str] = Field(
        default_factory=lambda: ["artist-arranged", "insured-courier", "local-pickup"]
    )
    likes: int = 0
    views: int = 0

class PurchaseRequest(BaseModel):
    artwork_id: str
    buyer_name: str
    buyer_email: str
    message: Optional[str] = ""
    status: Literal["new", "in_review", "accepted", "declined"] = "new"

# ---------------------------------------------------------------------------
# Supplies (traditional e-commerce items)
# ---------------------------------------------------------------------------
class Supply(BaseModel):
    title: str
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    category: str = Field(..., description="e.g., Brushes, Canvas, Paints")
    images: List[HttpUrl] = []
    stock: int = Field(0, ge=0)
    brand: Optional[str] = None

class OrderItem(BaseModel):
    supply_id: str
    title: str
    price: float
    quantity: int = Field(1, ge=1)

class Order(BaseModel):
    buyer_name: str
    buyer_email: str
    shipping_address: str
    items: List[OrderItem]
    total_amount: float = Field(..., ge=0)
    status: Literal["pending", "paid", "shipped", "delivered", "cancelled"] = "pending"

# ---------------------------------------------------------------------------
# Community / Social
# ---------------------------------------------------------------------------
class Post(BaseModel):
    author_id: str
    text: str
    images: List[HttpUrl] = []
    tags: List[str] = []
    likes: int = 0
    comments_count: int = 0

class Comment(BaseModel):
    post_id: str
    author_id: str
    text: str
    likes: int = 0
    created_at: Optional[datetime] = None
