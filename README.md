# Dashboard Kinerja Lelang

Implementasi studi kasus pada `Studi_Kasus_Visualisasi_Data_dengan_Python_Aset_dan_Lelang.pdf` menggunakan dataset yang disediakan.

## Mulai dari sini

1. Klik dua kali **`jalankan_dashboard.bat`** untuk membuka aplikasi Streamlit dengan enam tab di bagian atas, pilihan **Light/Dark**, sembilan grafik, lima KPI, dan enam filter. Environment `.venv` sudah disiapkan pada komputer ini.
2. Untuk komputer lain atau salinan ZIP, klik **`setup_environment.bat`** terlebih dahulu. Python 3.12 atau lebih baru dan internet untuk pemasangan awal diperlukan. Baca **[PANDUAN_ENVIRONMENT.md](PANDUAN_ENVIRONMENT.md)** untuk aktivasi `.venv` atau alternatif Conda melalui `environment.yml`.
3. Baca **[PENJELASAN_DAN_LANGKAH.md](PENJELASAN_DAN_LANGKAH.md)** untuk pertanyaan analitik, tahapan pengolahan, interpretasi, tiga temuan, tiga rekomendasi, dan panduan presentasi.
4. Buka **[dashboard_lelang.html](output/dashboard_lelang.html)** untuk melihat laporan seluruh dataset langsung di browser tanpa pemasangan atau internet.

![Ringkasan visual](output/ringkasan_visual.png)

Tab **Ringkasan**, **Wilayah**, **Aset**, **Proses & Data**, **Tindak Lanjut**, dan **Detail Lot** membantu pembaca langsung menuju analisis yang diperlukan. Tab Wilayah mempunyai pilihan Kanwil/KPKNL/Jenis Lelang. Ganti Light/Dark melalui pilihan **Tampilan** di kanan atas; cakupan filter tetap sama. Detail lot ditampilkan 50 baris per halaman, sedangkan CSV memuat seluruh hasil filter dan pencarian.

## Menjalankan secara manual

Jalankan dari folder `visualisasi-lelang`:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m streamlit run src/app.py
```

Buka alamat lokal yang ditampilkan, biasanya `http://localhost:8501`. Untuk menghentikan aplikasi, tekan `Ctrl+C` pada jendela terminalnya.

`requirements-lock.txt` mengunci versi paket hasil pengujian. `requirements.txt` mencatat dependensi langsung dengan rentang versi. Folder `.venv` dan `.packages` tidak disertakan dalam paket ZIP karena environment perlu dibuat ulang pada komputer tujuan.

## Membuat ulang laporan

```powershell
.\.venv\Scripts\python.exe src/exploration.py
```

Ekspor PNG grafik melalui Kaleido memerlukan Chrome/Chromium. Jika Chrome belum tersedia, gunakan:

```powershell
.\.venv\Scripts\python.exe src/exploration.py --skip-chart-png
```

HTML, ringkasan visual, CSV, dan JSON tetap dihasilkan oleh opsi tersebut. Grafik di Streamlit tidak memerlukan Kaleido atau Chrome.

## Pemeriksaan

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

File sumber tidak diubah. Data adalah bahan latihan; proporsi LAKU dalam dataset bukan tingkat keberhasilan lelang resmi.
