from locust import HttpUser, task, between


class PerpustakaanUser(HttpUser):
    # Jeda antar-task per pengguna virtual.
    wait_time = between(1, 3)

    @task(4)
    def list_buku(self):
        self.client.get("/resource/", name="GET /resource/")

    @task(2)
    def detail_buku(self):
        self.client.get("/resource/1", name="GET /resource/{id}")

    @task(1)
    def histori_transaksi(self):
        self.client.get("/transaction/", name="GET /transaction/")
