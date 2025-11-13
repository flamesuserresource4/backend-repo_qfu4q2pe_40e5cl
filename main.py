import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import User, Artwork, PurchaseRequest, Supply, Order, Post, Comment

app = FastAPI(title="ArtLink - Marketplace & Community for Artists")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"name": "ArtLink", "status": "ok"}

# ---------------------------------------------------------------------------
# Utility response models
# ---------------------------------------------------------------------------
class CreateResponse(BaseModel):
    id: str

# ---------------------------------------------------------------------------
# Accounts (basic create + list)
# ---------------------------------------------------------------------------
@app.post("/api/users", response_model=CreateResponse)
def create_user(user: User):
    new_id = create_document("user", user)
    return {"id": new_id}

@app.get("/api/users")
def list_users():
    return get_documents("user")

# ---------------------------------------------------------------------------
# Artwork showcase: present art as stories + inquiry flow
# ---------------------------------------------------------------------------
@app.post("/api/artworks", response_model=CreateResponse)
def create_artwork(artwork: Artwork):
    new_id = create_document("artwork", artwork)
    return {"id": new_id}

@app.get("/api/artworks")
def list_artworks(tag: Optional[str] = None):
    filt = {"tags": {"$in": [tag]}} if tag else {}
    return get_documents("artwork", filt, limit=50)

@app.post("/api/purchase-requests", response_model=CreateResponse)
def create_purchase_request(req: PurchaseRequest):
    new_id = create_document("purchaserequest", req)
    return {"id": new_id}

# ---------------------------------------------------------------------------
# Supplies store (classic e-commerce behavior for stationery)
# ---------------------------------------------------------------------------
@app.post("/api/supplies", response_model=CreateResponse)
def create_supply(supply: Supply):
    new_id = create_document("supply", supply)
    return {"id": new_id}

@app.get("/api/supplies")
def list_supplies(category: Optional[str] = None):
    filt = {"category": category} if category else {}
    return get_documents("supply", filt, limit=100)

class OrderInput(BaseModel):
    buyer_name: str
    buyer_email: str
    shipping_address: str
    items: List[dict]

@app.post("/api/orders", response_model=CreateResponse)
def create_order(order: OrderInput):
    # compute total
    total = 0.0
    for item in order.items:
        price = float(item.get("price", 0))
        qty = int(item.get("quantity", 1))
        total += price * qty
    order_doc = Order(
        buyer_name=order.buyer_name,
        buyer_email=order.buyer_email,
        shipping_address=order.shipping_address,
        items=order.items,  # type: ignore
        total_amount=total,
        status="pending",
    )
    new_id = create_document("order", order_doc)
    return {"id": new_id}

@app.get("/api/orders")
def list_orders():
    return get_documents("order", {}, limit=50)

# ---------------------------------------------------------------------------
# Community / Social
# ---------------------------------------------------------------------------
@app.post("/api/posts", response_model=CreateResponse)
def create_post(post: Post):
    new_id = create_document("post", post)
    return {"id": new_id}

@app.get("/api/posts")
def list_posts(tag: Optional[str] = None):
    filt = {"tags": {"$in": [tag]}} if tag else {}
    return get_documents("post", filt, limit=50)

@app.post("/api/comments", response_model=CreateResponse)
def create_comment(comment: Comment):
    new_id = create_document("comment", comment)
    return {"id": new_id}

@app.get("/api/comments")
def list_comments(post_id: str):
    return get_documents("comment", {"post_id": post_id}, limit=100)

# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------
@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
