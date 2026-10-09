# Hasil verifikasi dashboard

Tanggal pemeriksaan: 09/10/2026 10:25 WIT.

## Hasil akhir

- **8 pengujian lulus** dalam environment `.venv`: 7 pengujian pengolahan data dan 1 pengujian aplikasi yang mencakup beberapa skenario filter. Log tersedia di [hasil_pengujian.txt](hasil_pengujian.txt).
- `setup_environment.bat --no-pause` berhasil dijalankan dengan 51 paket yang dikunci. Pemeriksaan `pip check` menghasilkan **No broken requirements found**.
- Python **3.12.14**, Windows 64-bit, `include-system-site-packages = false`.
- Dashboard Streamlit berhasil ditampilkan di browser lokal dengan lima kartu KPI dan enam filter. Server pratinjau memakai `http://127.0.0.1:8502`; peluncur biasanya memakai port 8501.
- Sembilan PNG grafik, satu ringkasan visual, laporan HTML, CSV, dan JSON berhasil dibuat. Gambar diperiksa integritasnya; semua PNG grafik mempunyai latar putih.
- HTML memuat sembilan grafik dan pustaka Plotly tertanam, tanpa ketergantungan CDN Plotly.
- Detail CSV berisi 2.000 baris dan hanya 11 kolom operasional yang dipilih.
- Salinan workbook proyek identik dengan sumber berdasarkan SHA-256: `7de80eb7952524ce3e3b26a3ff16d396dfa3dca67dd4d63ff3ad4213946a7112`.

## Cakupan pengujian

| Pemeriksaan | Hasil |
|---|---|
| Total lot, status, limit, pokok, dan empat komponen bea terhadap sumber | Lulus |
| Filter wilayah/unit/status dibandingkan pemilihan independen | Lulus |
| Tanggal akhir mencakup timestamp malam | Lulus |
| Bulan parsial dan hari cakupan | Lulus |
| Durasi tetap mempertahankan pecahan hari | Lulus |
| Seluruh pokok kosong tampil sebagai tidak tersedia | Lulus |
| Pilihan KPKNL dibersihkan saat Kanwil tidak cocok | Lulus |
| Kombinasi tanpa hasil dan tombol atur ulang | Lulus |
| Kolom identitas tidak masuk tabel detail/CSV hasil | Lulus |

## Versi pustaka utama

| Pustaka | Versi |
|---|---|
| streamlit | 1.65.0 |
| pandas | 3.0.6 |
| plotly | 7.1.0 |
| numpy | 2.5.3 |
| openpyxl | 3.1.5 |
| matplotlib | 3.11.2 |
| kaleido | 1.5.0 |

Versi seluruh 51 paket tersedia di `requirements-lock.txt`. `pathlib` merupakan pustaka bawaan Python. Environment Conda tersedia sebagai alternatif konfigurasi; Conda tidak dijalankan pada pemeriksaan ini.

## Kontrol angka seluruh dataset

| Ukuran | Hasil |
|---|---:|
| Lot | 2.000 |
| Lot LAKU | 240 |
| Status kosong | 258 |
| Total limit | Rp410.171.717.355 |
| Pokok tercatat | Rp51.258.617.539 |
| Total bea tercatat | Rp2.413.656.000 |

Data merupakan bahan latihan. Proporsi LAKU memakai seluruh observasi terpilih, sehingga bukan tingkat keberhasilan resmi. Nilai kosong tidak diisi sebagai realisasi nol. Makna outcome final, tanggal pembaruan status, dan SLA perlu dikonfirmasi kepada pemilik proses.
