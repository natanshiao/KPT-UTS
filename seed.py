import asyncio
import aiosqlite

from database import DATABASE_NAME, init_db

# Data, data, data.
BOOKS = [
    ("Belajar Python", "Budi Santoso", "BK001", "Alam", 2023, 80),
    ("Dasar Menjadi Presiden", "Siti Aminah", "BK002", "Politik", 2022, 8),
    ("Algoritma dan Pemrograman", "Andi Wijaya", "BK003", "Teknologi", 2021, 6),
    ("Jaringan Kartel", "Rina Putri", "BK004", "Geografis", 2020, 4),
    ("Pemrograman Web", "Dewi Lestari", "BK005", "Teknologi", 2024, 7),
    ("Islam Ala Prabowo", "Prabowo Subianto", "BK006", "Agama", 2026, 67),
    ("Clean Code", "Robert C. Martin", "BK007", "Teknologi", 2008, 3),
    ("Atomic Habits", "James Clear", "BK008", "Pengembangan Diri", 2018, 9),
    ("Laskar Pelangi", "Andrea Hirata", "BK009", "Novel", 2005, 10),
    ("Bumi Manusia", "Pramoedya Ananta Toer", "BK010", "Novel", 1980, 6),
    ("Sejarah Ijazah Asli", "Jokowi Dodo", "BK011", "Sejarah", 2026, 67),
]


async def main():
    await init_db()
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.executemany(
            """
            INSERT OR IGNORE INTO rak_buku
            (nama_buku, penulis_buku, kode_buku, kategori, tahun_terbit, stok)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            BOOKS,
        )
        await db.commit()

        cursor = await db.execute("SELECT COUNT(*) FROM rak_buku")
        count = (await cursor.fetchone())[0]
        print(f"Seed selesai. Total data buku di database: {count}")


if __name__ == "__main__":
    asyncio.run(main())
