"""
Uji race condition peminjaman serentak.
Jalankan server terlebih dahulu, lalu: python test_race.py
Uji ini mengurangi stok BK001 sampai habis; jalankan seed/reset stok sebelum mengulang.
"""
import asyncio
import httpx

BASE_URL = "http://127.0.0.1:8000"
REQUEST_COUNT = 20


async def main():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as client:
        response = await client.get("/resource/")
        response.raise_for_status()
        books = response.json()
        book = next((item for item in books if item["kode_buku"] == "BK001"), None)

        if book is None:
            raise RuntimeError("BK001 tidak ditemukan. Jalankan python seed.py terlebih dahulu.")

        initial_stock = book["stok"]
        if initial_stock <= 0:
            raise RuntimeError("Stok BK001 sudah 0. Tambahkan stok sebelum menguji.")

        # Semua request mencoba meminjam 1 eksemplar pada waktu hampir bersamaan.
        responses = await asyncio.gather(*[
            client.post(
                "/transaction/borrow",
                json={"buku_id": book["id"], "jumlah": 1},
            )
            for _ in range(REQUEST_COUNT)
        ])

        success = sum(1 for item in responses if item.status_code == 201)
        rejected = sum(1 for item in responses if item.status_code == 409)
        after = await client.get(f"/resource/{book['id']}")
        after.raise_for_status()
        final_stock = after.json()["stok"]

        print(f"Stok awal       : {initial_stock}")
        print(f"Request berhasil: {success}")
        print(f"Ditolak (stok)  : {rejected}")
        print(f"Stok akhir      : {final_stock}")
        print("PASS: stok tidak negatif." if final_stock >= 0 else "FAIL: stok negatif!")

        if success != min(initial_stock, REQUEST_COUNT) or final_stock != max(0, initial_stock - REQUEST_COUNT):
            print("Periksa hasil: ada request lain yang mungkin mengubah stok selama pengujian.")


if __name__ == "__main__":
    asyncio.run(main())
