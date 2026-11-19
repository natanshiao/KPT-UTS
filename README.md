Link\"LINK YT"
# UTS KOMPUTASI PARAREL DAN TERDISTRIBUSI

**Nama: Denathan**
**NIM: 231220024**
**Kelas: 31**
**Mata Kuliah: Komputasi Pararel dan Terdistribusi**

***Tugas Ini di Assist oleh AI, Mustahil dilakukan sendiri Dalam waktu singkat dan dalam Waktu Kerja Praktik, Tidak semua komponen pada repositori ini AI Assisted***

## Persiapan pada host sistem
Download python dan sqlite jika belum ada
> ARCH LINUX
```
sudo pacman -S python sqlite python-pip --noconfirm
```

> UBUNTU
```
sudo apt python3 sqlite -y
```

## Buat Env
> buat python env
```
python -m venv .venv
```

## Sourcing custom env
pilih sesuai SHELL yang sedang di gunakan
> Source py .env (bash/zsh)
```
source .venv/bin/activate
```

> Source py .env (fish)
```
source .venv/bin/activate.fish
```

## pip
> Update pip
```
pip install --upgrade pip
```

> install requirement yang di perlukan (besertakan depedensi)
```
pip install -r requirement.txt
```

## Cara Menggunakan
> Siapkan seed
```
python seed.py
```

> Jalankan API
```
uvicorn main:app --host 127.0.0.1 --port 8000
```

> test race (transaction berada routes/transaction*) dan di deklarasi pada main.py
```
python test_race.py
```

## Benchmark
> Jalankan API
```
uvicorn main:app --host 127.0.0.1 --port 8000 --workers N 
```
Ganti N dengan banyak workers yang di inginkan

> jalakan locust
```
locust -f locustfile.py
```


## Download paket secara manual di sini
Python
<p><a href="https://www.python.org/downloads/" target="_blank">Download</a></p>
Sqlite
<p><a href="https://sqlite.org/download.html" target="_blank">Download</a></p>

