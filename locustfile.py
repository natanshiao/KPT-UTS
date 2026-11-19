
from locust import HttpUser, task, between


class PerpustakaanUser(HttpUser):
    # Jeda antar-task untuk setiap pengguna virtual.
    wait_time = between(1, 3)

    @task(4)
    def list_buku(self):
        # Bobot 4: menguji endpoint daftar buku.
        with self.client.get(
            "/resource/?skip=0&limit=10",
            name="GET /resource/",
            catch_response=True
        ) as response:

            if response.status_code != 200:
                response.failure(
                    f"Gagal mengambil daftar buku: {response.status_code}"
                )

    @task(2)
    def detail_buku(self):
        # Bobot 2: menguji detail buku dengan ID 1.
        with self.client.get(
            "/resource/1",
            name="GET /resource/{id}",
            catch_response=True
        ) as response:

            if response.status_code != 200:
                response.failure(
                    f"Gagal mengambil detail buku: {response.status_code}"
                )

    @task(1)
    def histori_transaksi(self):
        # Bobot 1: menguji histori transaksi.
        with self.client.get(
            "/transaction/?skip=0&limit=10",
            name="GET /transaction/",
            catch_response=True
        ) as response:

            if response.status_code != 200:
                response.failure(
                    f"Gagal mengambil histori transaksi: {response.status_code}"
                )
