import sqlite3

# Membuka database yang digunakan aplikasi.
conn = sqlite3.connect("uts-perpustakaan.db")

# Memeriksa struktur tabel.
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(rak_buku)")

columns = cursor.fetchall()

print("Struktur tabel rak_buku:")

for column in columns:
    print(column)

conn.close()
