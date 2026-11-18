from pathlib import Path
import aiosqlite

# Lokasi database selalu relatif terhadap file ini, bukan current working directory.
DATABASE_NAME = Path(__file__).resolve().parent / "uts-perpustakaan.db"

CREATE_RESOURCE_TABLE = """
CREATE TABLE IF NOT EXISTS rak_buku (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_buku TEXT NOT NULL,
    penulis_buku TEXT NOT NULL,
    kode_buku TEXT NOT NULL,
    kategori TEXT NOT NULL,
    tahun_terbit INTEGER NOT NULL,
    stok INTEGER NOT NULL DEFAULT 0 CHECK (stok >= 0)
);
"""

CREATE_TRANSACTION_TABLE = """
CREATE TABLE IF NOT EXISTS transaksi_buku (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    buku_id INTEGER NOT NULL,
    jenis TEXT NOT NULL CHECK (jenis IN ('pinjam', 'kembali')),
    jumlah INTEGER NOT NULL CHECK (jumlah > 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (buku_id) REFERENCES rak_buku(id)
);
"""


async def init_db():
    """Membuat tabel dan menambahkan kolom yang belum ada pada database lama."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        await db.execute("PRAGMA busy_timeout = 5000")
        await db.execute(CREATE_RESOURCE_TABLE)

        # Migrasi ringan untuk tabel rak_buku versi lama (3 kolom).
        cursor = await db.execute("PRAGMA table_info(rak_buku)")
        existing_columns = {row[1] for row in await cursor.fetchall()}

        migrations = {
            "kode_buku": "ALTER TABLE rak_buku ADD COLUMN kode_buku TEXT",
            "kategori": "ALTER TABLE rak_buku ADD COLUMN kategori TEXT NOT NULL DEFAULT 'Umum'",
            "tahun_terbit": "ALTER TABLE rak_buku ADD COLUMN tahun_terbit INTEGER NOT NULL DEFAULT 2000",
            "stok": "ALTER TABLE rak_buku ADD COLUMN stok INTEGER NOT NULL DEFAULT 0",
        }
        for column, sql in migrations.items():
            if column not in existing_columns:
                await db.execute(sql)

        # Beri kode unik pada baris lama yang belum memiliki kode buku.
        await db.execute("""
            UPDATE rak_buku
            SET kode_buku = 'LEGACY-' || id
            WHERE kode_buku IS NULL OR kode_buku = ''
        """)
        await db.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_rak_buku_kode
            ON rak_buku(kode_buku)
        """)

        await db.execute(CREATE_TRANSACTION_TABLE)
        await db.commit()
