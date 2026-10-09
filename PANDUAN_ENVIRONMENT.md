# Environment Python untuk dashboard

Dashboard memakai environment terpisah agar dependensi proyek tidak bercampur dengan proyek lain. Aplikasi menggunakan `streamlit`, `pandas`, `plotly.express`, dan `pathlib.Path`. `pathlib` tersedia langsung di Python dan tidak perlu dipasang terpisah.

## Cara termudah di Windows

1. Buka folder `visualisasi-lelang`.
2. Klik dua kali `setup_environment.bat`. File ini membuat `.venv` dan memasang dependensi dari `requirements-lock.txt`. Pemasangan awal memerlukan internet dan Python 3.12 atau lebih baru.
3. Setelah muncul **Environment siap**, klik dua kali `jalankan_dashboard.bat`.
4. Dashboard terbuka di browser. Tekan `Ctrl+C` di jendela terminal untuk menghentikannya.

Pada komputer tempat hasil ini dibuat, `.venv` sudah disiapkan. Untuk salinan ZIP atau komputer lain, buat ulang environment melalui langkah di atas. Folder environment berisi jalur khusus komputer sehingga tidak disertakan dalam ZIP.

## Pilihan A — virtual environment

Jalankan dari folder proyek. Python 3.12 digunakan pada pengujian hasil ini. Versi NumPy dan ContourPy yang dikunci memerlukan Python minimal 3.12; Python 3.12 menjadi pilihan yang disarankan untuk membuat ulang hasil.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m streamlit run src/app.py
```

Aktivasi opsional di PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m streamlit run src/app.py
deactivate
```

Jika kebijakan PowerShell membatasi aktivasi, gunakan perintah dengan jalur lengkap `.\.venv\Scripts\python.exe` di atas. Aktivasi tidak wajib untuk menjalankan aplikasi. Untuk Command Prompt, gunakan `.venv\Scripts\activate.bat`.

## Pilihan B — Conda

Jika Anaconda atau Miniconda sudah tersedia, `environment.yml` menyediakan alternatif environment bernama `visualisasi-lelang`:

```powershell
conda env create -f environment.yml
conda activate visualisasi-lelang
python -m streamlit run src/app.py
conda deactivate
```

Pilih salah satu cara. Environment `.venv` dan Conda tidak perlu diaktifkan bersamaan. Konfigurasi Conda disediakan sebagai alternatif; pengujian dashboard dilakukan dengan Python di `.venv`.

## Isi konfigurasi

| File/folder | Kegunaan |
|---|---|
| `.venv/` | Environment lokal yang siap dipakai pada komputer ini |
| `requirements.txt` | Daftar dependensi langsung beserta rentang versi yang didukung |
| `requirements-lock.txt` | Seluruh versi paket yang dipasang untuk hasil pengujian ini |
| `environment.yml` | Definisi environment Conda dengan Python 3.12 |
| `setup_environment.bat` | Membuat `.venv`, memasang dependensi, dan memeriksa kompatibilitas paket |
| `jalankan_dashboard.bat` | Menjalankan Streamlit dengan Python dari `.venv` |
| `.streamlit/config.toml` | Tema, alamat server lokal, dan konfigurasi Streamlit |

Tidak diperlukan akun, kunci API, atau file `.env`. Dataset dibaca dari `data/Dummy_Kinerja_Lelang.xlsx` berdasarkan lokasi proyek melalui `Path`, sehingga tidak perlu mengubah jalur data saat folder dipindahkan.

## Memeriksa dan membuat ulang hasil

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe src/exploration.py
```

Ekspor sembilan PNG menggunakan Kaleido dan memerlukan Google Chrome/Chromium. Dashboard Streamlit tidak memerlukan Chrome khusus untuk menampilkan grafik. Jika Chrome belum dipasang, buat ulang HTML, CSV, JSON, dan ringkasan visual dengan:

```powershell
.\.venv\Scripts\python.exe src/exploration.py --skip-chart-png
```

Versi Python, versi paket, serta hasil pemeriksaan tercatat pada `output/hasil_verifikasi.md`.
