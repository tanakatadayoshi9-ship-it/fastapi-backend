from fastapi import APIRouter, HTTPException, Query
import aiosqlite

from app.schemas import (
    ItemCreate,
    ItemUpdate,
    ItemResponse
)

DB_PATH = "app.db"

router = APIRouter(
    prefix="/items",
    tags=["Items"]
)

# =====================
# SEARCH (باید بالا باشد)
# =====================
@router.get("/search", response_model=list[ItemResponse])
async def search_items(q: str = Query(..., min_length=1)):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT id, title, description
            FROM items
            WHERE title LIKE ? OR description LIKE ?
            """,
            (f"%{q}%", f"%{q}%")
        )
        rows = await cursor.fetchall()

        return [
            {"id": r[0], "title": r[1], "description": r[2]}
            for r in rows
        ]


# =====================
# CREATE
# =====================
@router.post("/", response_model=ItemResponse)
async def create_item(item: ItemCreate):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO items (title, description)
            VALUES (?, ?)
            """,
            (item.title, item.description)
        )
        await db.commit()

        return {
            "id": cursor.lastrowid,
            "title": item.title,
            "description": item.description
        }


# =====================
# READ ALL + PAGINATION + SORTING
# =====================
@router.get("/", response_model=list[ItemResponse])
async def get_items(
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=1, le=100),
    sort_by: str = Query("id"),
    order: str = Query("asc")
):
    allowed_sort_fields = {"id", "title"}
    if sort_by not in allowed_sort_fields:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    if order not in {"asc", "desc"}:
        raise HTTPException(status_code=400, detail="Invalid order")

    offset = (page - 1) * limit

    query = f"""
        SELECT id, title, description
        FROM items
        ORDER BY {sort_by} {order.upper()}
        LIMIT ? OFFSET ?
    """

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(query, (limit, offset))
        rows = await cursor.fetchall()

        return [
            {"id": r[0], "title": r[1], "description": r[2]}
            for r in rows
        ]


# =====================
# READ BY ID (داینامیک – پایین)
# =====================
@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, title, description FROM items WHERE id = ?",
            (item_id,)
        )
        row = await cursor.fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="Item not found")

        return {"id": row[0], "title": row[1], "description": row[2]}


# =====================
# UPDATE
# =====================
@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, item: ItemUpdate):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id FROM items WHERE id = ?",
            (item_id,)
        )
        if await cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Item not found")

        await db.execute(
            """
            UPDATE items
            SET title = ?, description = ?
            WHERE id = ?
            """,
            (item.title, item.description, item_id)
        )
        await db.commit()

        return {
            "id": item_id,
            "title": item.title,
            "description": item.description
        }


# =====================
# DELETE
# =====================
@router.delete("/{item_id}")
async def delete_item(item_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id FROM items WHERE id = ?",
            (item_id,)
        )
        if await cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Item not found")

        await db.execute(
            "DELETE FROM items WHERE id = ?",
            (item_id,)
        )
        await db.commit()

        return {"message": "Item deleted successfully"}






























