import asyncio
import aiosqlite
import httpx

from database import DATABASE_NAME

BASE_URL = "http://127.0.0.1:8000"

# ID buku yang digunakan untuk pengujian.
BUKU_ID = 1


async def reset_stok():
    """Mengembalikan stok buku menjadi 1."""

    async with aiosqlite.connect(DATABASE_NAME) as db:

        cursor = await db.execute(
            "UPDATE rak_buku SET stok = 1 WHERE id = ?",
            (BUKU_ID,)
        )

        # Memastikan buku dengan ID tersebut tersedia.
        if cursor.rowcount == 0:
            raise ValueError(
                f"Buku dengan ID {BUKU_ID} tidak ditemukan."
                " Jalankan seed.py terlebih dahulu."
            )

        await db.commit()

    print("Stok awal berhasil diatur menjadi 1.")


async def pinjam(client, nomor):
    """Mengirim permintaan peminjaman secara asynchronous."""

    response = await client.post(
        f"{BASE_URL}/transaction/borrow",
        params={
            "buku_id": BUKU_ID,
            "jumlah": 1
        }
    )

    print(f"\nTransaksi {nomor}")
    print(f"Status HTTP : {response.status_code}")
    print(f"Response    : {response.text}")

    return response.status_code


async def cek_stok():
    """Memeriksa stok akhir pada database SQLite."""

    async with aiosqlite.connect(DATABASE_NAME) as db:

        cursor = await db.execute(
            "SELECT stok FROM rak_buku WHERE id = ?",
            (BUKU_ID,)
        )

        result = await cursor.fetchone()

        if result is None:
            raise ValueError("Buku tidak ditemukan.")

        return result[0]


async def main():

    # Mengatur ulang stok sebelum setiap pengujian.
    await reset_stok()

    async with httpx.AsyncClient(timeout=10.0) as client:

        print("\nMengirim dua transaksi secara bersamaan...")

        # Menjalankan dua request secara concurrent.
        results = await asyncio.gather(
            pinjam(client, 1),
            pinjam(client, 2)
        )

    # Memeriksa stok setelah kedua request selesai.
    stok_akhir = await cek_stok()

    print("\n========== HASIL PENGUJIAN ==========")
    print("Status transaksi :", results)
    print("Stok akhir       :", stok_akhir)
    print("=====================================")


if __name__ == "__main__":
    asyncio.run(main())
