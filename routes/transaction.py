import aiosqlite
from fastapi import APIRouter, HTTPException, status

from database import DATABASE_NAME
from models import TransactionRequest

router = APIRouter()


async def _change_stock(payload: TransactionRequest, jenis: str):
    """Mengubah stok dan mencatat transaksi dalam satu transaksi SQL atomik."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        await db.execute("PRAGMA busy_timeout = 5000")

        try:
            # BEGIN IMMEDIATE mengambil reserved write lock sebelum membaca stok.
            await db.execute("BEGIN IMMEDIATE")

            cursor = await db.execute(
                "SELECT stok FROM rak_buku WHERE id = ?", (payload.buku_id,)
            )
            book = await cursor.fetchone()
            if book is None:
                raise HTTPException(status_code=404, detail="Buku tidak ditemukan")

            if jenis == "pinjam":
                # Syarat stok >= jumlah mencegah stok menjadi negatif.
                if book[0] < payload.jumlah:
                    raise HTTPException(status_code=409, detail="Stok buku tidak mencukupi")
                await db.execute(
                    "UPDATE rak_buku SET stok = stok - ? WHERE id = ? AND stok >= ?",
                    (payload.jumlah, payload.buku_id, payload.jumlah),
                )
            else:
                await db.execute(
                    "UPDATE rak_buku SET stok = stok + ? WHERE id = ?",
                    (payload.jumlah, payload.buku_id),
                )

            cursor = await db.execute(
                """
                INSERT INTO transaksi_buku (buku_id, jenis, jumlah)
                VALUES (?, ?, ?)
                """,
                (payload.buku_id, jenis, payload.jumlah),
            )
            transaction_id = cursor.lastrowid
            await db.commit()

            db.row_factory = aiosqlite.Row
            result = await db.execute(
                "SELECT * FROM transaksi_buku WHERE id = ?", (transaction_id,)
            )
            return dict(await result.fetchone())

        except HTTPException:
            await db.rollback()
            raise
        except aiosqlite.Error as exc:
            await db.rollback()
            raise HTTPException(
                status_code=500, detail="Transaksi database gagal"
            ) from exc


@router.post("/borrow", status_code=status.HTTP_201_CREATED)
async def borrow_book(payload: TransactionRequest):
    return await _change_stock(payload, "pinjam")


@router.post("/return", status_code=status.HTTP_201_CREATED)
async def return_book(payload: TransactionRequest):
    return await _change_stock(payload, "kembali")


@router.get("/")
async def get_transactions(skip: int = 0, limit: int = 20):
    # Daftar histori transaksi terbaru.
    async with aiosqlite.connect(DATABASE_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT t.*, b.nama_buku
            FROM transaksi_buku AS t
            JOIN rak_buku AS b ON b.id = t.buku_id
            ORDER BY t.id DESC LIMIT ? OFFSET ?
            """,
            (limit, skip),
        )
        return [dict(row) for row in await cursor.fetchall()]
