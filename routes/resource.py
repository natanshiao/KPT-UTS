import aiosqlite
from fastapi import APIRouter, HTTPException, Query, status

from database import DATABASE_NAME
from models import BukuCreate, BukuUpdate

router = APIRouter()


@router.get("/")
async def get_all_buku(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
):
    # row_factory membuat setiap baris dapat diubah menjadi dict.
    async with aiosqlite.connect(DATABASE_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM rak_buku ORDER BY id LIMIT ? OFFSET ?",
            (limit, skip),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


@router.get("/{buku_id}")
async def get_buku(buku_id: int):
    async with aiosqlite.connect(DATABASE_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM rak_buku WHERE id = ?", (buku_id,)
        )
        row = await cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Buku tidak ditemukan")
    return dict(row)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_buku(payload: BukuCreate):
    values = payload.model_dump()
    async with aiosqlite.connect(DATABASE_NAME) as db:
        db.row_factory = aiosqlite.Row
        try:
            cursor = await db.execute(
                """
                INSERT INTO rak_buku
                (nama_buku, penulis_buku, kode_buku, kategori, tahun_terbit, stok)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                tuple(values.values()),
            )
            await db.commit()
            new_id = cursor.lastrowid
            result = await db.execute(
                "SELECT * FROM rak_buku WHERE id = ?", (new_id,)
            )
            row = await result.fetchone()
        except aiosqlite.IntegrityError as exc:
            await db.rollback()
            raise HTTPException(status_code=422, detail="Kode buku sudah digunakan") from exc

    return dict(row)


@router.put("/{buku_id}")
async def update_buku(buku_id: int, payload: BukuUpdate):
    values = payload.model_dump()
    async with aiosqlite.connect(DATABASE_NAME) as db:
        db.row_factory = aiosqlite.Row
        try:
            cursor = await db.execute(
                """
                UPDATE rak_buku
                SET nama_buku = ?, penulis_buku = ?, kode_buku = ?,
                    kategori = ?, tahun_terbit = ?, stok = ?
                WHERE id = ?
                """,
                (*values.values(), buku_id),
            )
            if cursor.rowcount == 0:
                await db.rollback()
                raise HTTPException(status_code=404, detail="Buku tidak ditemukan")
            await db.commit()
            result = await db.execute(
                "SELECT * FROM rak_buku WHERE id = ?", (buku_id,)
            )
            row = await result.fetchone()
        except aiosqlite.IntegrityError as exc:
            await db.rollback()
            raise HTTPException(status_code=422, detail="Kode buku sudah digunakan") from exc

    return dict(row)


@router.delete("/{buku_id}")
async def delete_buku(buku_id: int):
    async with aiosqlite.connect(DATABASE_NAME) as db:
        cursor = await db.execute("DELETE FROM rak_buku WHERE id = ?", (buku_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Buku tidak ditemukan")
        await db.commit()

    return {"message": "Buku berhasil dihapus", "id": buku_id}
