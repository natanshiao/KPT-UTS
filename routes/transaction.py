import asyncio
import aiosqlite

from fastapi import APIRouter, HTTPException
from database import DATABASE_NAME

router = APIRouter(
    prefix="/transaction",
    tags=["Transaction"]
)

# Endpoint untuk mengambil histori transaksi.
@router.get("/")
async def histori_transaksi(skip: int = 0, limit: int = 10):

    async with aiosqlite.connect(DATABASE_NAME) as db:

        # Mengambil histori transaksi beserta nama buku.
        db.row_factory = aiosqlite.Row

        cursor = await db.execute("""
            SELECT
                t.id,
                t.buku_id,
                r.nama_buku,
                t.jenis,
                t.jumlah,
                t.created_at
            FROM transaksi_buku AS t
            LEFT JOIN rak_buku AS r
                ON t.buku_id = r.id
            ORDER BY t.id DESC
            LIMIT ? OFFSET ?
        """, (limit, skip))

        rows = await cursor.fetchall()

        # Mengubah hasil query menjadi JSON.
        return [dict(row) for row in rows]

@router.post("/borrow", status_code=201)
async def borrow_book(buku_id: int, jumlah: int = 1):

    # Validasi jumlah peminjaman.
    if jumlah <= 0:
        raise HTTPException(
            status_code=422,
            detail="Jumlah peminjaman harus lebih dari 0"
        )

    async with aiosqlite.connect(DATABASE_NAME) as db:

        # Membaca stok awal buku.
        cursor = await db.execute(
            "SELECT stok FROM rak_buku WHERE id = ?",
            (buku_id,)
        )

        book = await cursor.fetchone()

        if book is None:
            raise HTTPException(
                status_code=404,
                detail="Buku tidak ditemukan"
            )

        stok_sekarang = book[0]

        # Memeriksa stok sebelum peminjaman.
        if stok_sekarang < jumlah:
            raise HTTPException(
                status_code=409,
                detail="Stok buku habis"
            )

        # Memberi kesempatan request lain membaca stok yang sama.
        await asyncio.sleep(0.01)

        # Mengurangi stok secara langsung di SQLite.
        # Tidak menggunakan asyncio.Lock.
        await db.execute(
            """
            UPDATE rak_buku
            SET stok = stok - ?
            WHERE id = ?
            """,
            (jumlah, buku_id)
        )

        # Mencatat transaksi peminjaman.
        await db.execute("""
            INSERT INTO transaksi_buku (buku_id, jenis, jumlah)
            VALUES (?, 'pinjam', ?)
        """, (buku_id, jumlah))

        await db.commit()

        # Membaca stok setelah pengurangan.
        cursor = await db.execute(
            "SELECT stok FROM rak_buku WHERE id = ?",
            (buku_id,)
        )

        stok_akhir = (await cursor.fetchone())[0]

        return {
            "message": "Transaksi berhasil",
            "buku_id": buku_id,
            "stok_akhir": stok_akhir
        }
