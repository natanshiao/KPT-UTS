from pydantic import BaseModel, Field, ConfigDict


class BukuCreate(BaseModel):
    # Field constraints dijalankan otomatis oleh Pydantic.
    nama_buku: str = Field(min_length=1, max_length=200)
    penulis_buku: str = Field(min_length=1, max_length=150)
    kode_buku: str = Field(min_length=1, max_length=30)
    kategori: str = Field(min_length=1, max_length=80)
    tahun_terbit: int = Field(ge=1000, le=2100)
    stok: int = Field(ge=0)


class BukuUpdate(BukuCreate):
    pass


class BukuResponse(BukuCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class TransactionRequest(BaseModel):
    buku_id: int = Field(gt=0)
    jumlah: int = Field(gt=0, le=1000)


class TransactionResponse(BaseModel):
    id: int
    buku_id: int
    jenis: str
    jumlah: int
    created_at: str
