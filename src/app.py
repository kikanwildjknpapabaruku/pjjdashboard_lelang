"""Jalankan dari folder proyek: python -m streamlit run src/app.py."""
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import html
from analysis import (by_region, diagnostics, filter_data,
                      load_data, metrics, monthly, number, quality, rupiah, safe_detail, stories)
from charts import (asset_chart, duration_chart, limit_chart, quality_chart, region_chart,
                    status_chart, trend_chart, type_chart, unit_chart)
from ui import page_css, table_html, themed_figure

BASE_DIR = Path(__file__).resolve().parents[1]
DATA = BASE_DIR / "data" / "Dummy_Kinerja_Lelang.xlsx"
px.defaults.template = "plotly_white"

st.set_page_config(page_title="Kinerja Lelang", page_icon="📊", layout="wide", initial_sidebar_state="expanded")


@st.cache_data(show_spinner="Membaca data lelang...")
def read_source(modified):
    return load_data(DATA)


try:
    df = read_source(DATA.stat().st_mtime_ns)
except (OSError, ValueError) as error:
    st.error(f"Data belum dapat dibaca: {error}")
    st.stop()

date_min, date_max = df.tgl_lelang.min().date(), df.tgl_lelang.max().date()

heading, appearance = st.columns([4, 1.2], vertical_alignment="center")
with heading:
    st.markdown('<div class="eyebrow">ANALITIK ASET DAN LELANG</div>', unsafe_allow_html=True)
    st.title("Kinerja Lelang")
with appearance:
    mode = st.radio("Tampilan", ["Light", "Dark"], horizontal=True, key="tampilan")
st.html(page_css(mode))


def reset_filters():
    for key in ["kanwil", "kpknl", "jenis", "aset", "status", "tanggal"]:
        st.session_state.pop(key, None)


with st.sidebar:
    st.markdown('<div class="eyebrow">STUDI KASUS PYTHON</div>', unsafe_allow_html=True)
    st.title("Cakupan analisis")
    st.caption("Pilihan kosong berarti semua kategori.")
    dates = st.date_input("Tanggal lelang", value=(date_min, date_max), min_value=date_min, max_value=date_max, key="tanggal", format="DD/MM/YYYY")
    kanwil = st.multiselect("Kanwil", sorted(df.kanwil_ringkas.unique()), key="kanwil")
    options = df[df.kanwil_ringkas.isin(kanwil)] if kanwil else df
    valid_units = sorted(options.kpknl.unique())
    if "kpknl" in st.session_state:
        st.session_state.kpknl = [v for v in st.session_state.kpknl if v in valid_units]
    kpknl = st.multiselect("KPKNL", valid_units, key="kpknl")
    jenis = st.multiselect("Jenis lelang", sorted(df.jenis_lelang.unique()), key="jenis")
    aset = st.multiselect("Kategori aset", sorted(df.kategori_aset.unique()), key="aset")
    status = st.multiselect("Status lelang", sorted(df.status_tampil.unique()), key="status")
    st.button("Atur ulang filter", on_click=reset_filters, width="stretch")
    st.divider()
    st.caption("Sumber: Dummy_Kinerja_Lelang.xlsx, sheet RAW Kinerja Lelang. Data latihan, bukan kinerja resmi.")
    st.caption("Tanggal pembaruan status tidak tersedia. Tanggal lelang tidak menunjukkan kapan status terakhir diperbarui.")

if len(dates) != 2:
    st.info("Lengkapi tanggal awal dan akhir untuk menampilkan dashboard.")
    st.stop()

view = filter_data(df, dates[0], dates[1], kanwil_ringkas=kanwil, kpknl=kpknl,
                   jenis_lelang=jenis, kategori_aset=aset, status_tampil=status)
m = metrics(view)
st.markdown(f'<div class="scope">{dates[0]:%d/%m/%Y} - {dates[1]:%d/%m/%Y} · {number(len(view))} dari {number(len(df))} lot · {view.kanwil.nunique()} Kanwil · {view.kpknl.nunique()} KPKNL</div>', unsafe_allow_html=True)
st.caption("Pilih tab untuk langsung menuju analisis. Semua tab dan unduhan mengikuti filter di sebelah kiri.")
if view.empty:
    st.warning("Tidak ada lot pada kombinasi filter ini. Longgarkan pilihan atau gunakan Atur ulang filter.")
    st.stop()
if status:
    st.info("Filter status aktif. Persentase LAKU menggunakan seluruh lot hasil filter sebagai denominator dan akan berubah saat status dipilih.")

def plot(fig, key):
    st.plotly_chart(themed_figure(fig, mode), width="stretch", key=key, theme=None)


def table(frame, label, names=None):
    st.html(table_html(frame, label, names))


tabs = st.tabs(["Ringkasan", "Wilayah", "Aset", "Proses & Data", "Tindak Lanjut", "Detail Lot"],
               key="halaman", on_change="rerun")

if tabs[0].open:
    with tabs[0]:
        values = [("Jumlah lot", number(m['lot']), "observasi pada cakupan terpilih"),
                  ("Total nilai limit", rupiah(m['limit']), "nilai limit tercatat"),
                  ("Lot berstatus LAKU", number(m['laku']), f"{number(m['laku_pct'], 1)}% dari observasi terpilih"),
                  ("Pokok lelang tercatat", rupiah(m['pokok']), f"tersedia pada {number(m['pokok_count'])} lot"),
                  ("Total bea tercatat", rupiah(m['bea']), "jumlah empat komponen bea")]
        for row in [values[:3], values[3:]]:
            for col, (label, value, help_text) in zip(st.columns(len(row)), row):
                col.metric(label, value)
                col.caption(help_text)
        st.caption("Proporsi LAKU bukan tingkat keberhasilan resmi. Pokok dan bea dijumlahkan dari nilai tersedia; nilai kosong tidak diimputasi sebagai realisasi nol.")
        cols = st.columns([1, 1.2])
        with cols[0]:
            st.subheader("Komposisi status lelang")
            plot(status_chart(view), "status_chart")
        with cols[1]:
            st.subheader("Pola volume lelang")
            granularity = st.radio("Interval waktu", ["Mingguan", "Bulanan"], horizontal=True,
                                   label_visibility="collapsed", key="interval")
            plot(trend_chart(view, granularity, dates[0], dates[1]), "trend_chart")
        st.caption("Minggu/bulan pada tepi jendela data dapat tercakup sebagian. LAKU dan tanpa status merupakan bagian dari semua lot.")
        with st.expander("Cakupan bulanan dan volume per hari kalender"):
            table(monthly(view, dates[0], dates[1]), "Cakupan bulanan",
                  {"lot_per_hari": "Lot per hari cakupan"})
            st.caption("Hari cakupan termasuk hari tanpa lot. Rasio ini bukan produktivitas hari kerja atau bukti tren musiman.")

if tabs[1].open:
    with tabs[1]:
        region_tabs = st.tabs(["Kanwil", "KPKNL", "Jenis Lelang"], key="wilayah_view", on_change="rerun")
        if region_tabs[0].open:
            with region_tabs[0]:
                st.subheader("Volume dan komposisi status menurut Kanwil")
                plot(region_chart(view), "region_chart")
                st.caption("Status lainnya: BELUM TAYANG, MULAI PENAWARAN, SELESAI PENAWARAN, TAP, serta status tambahan bila ada. Tidak diasumsikan sebagai outcome final.")
        if region_tabs[1].open:
            with region_tabs[1]:
                st.subheader("KPKNL: volume, proporsi LAKU, dan eksposur nilai")
                plot(unit_chart(view), "unit_chart")
                st.caption("Ukuran lingkaran = total nilai limit; warna = persentase tanpa status. Komposisi jenis dan tahap proses perlu ditelaah sebelum membandingkan kinerja.")
                with st.expander("Tabel perbandingan KPKNL"):
                    table(by_region(view, "kpknl"), "Perbandingan KPKNL")
        if region_tabs[2].open:
            with region_tabs[2]:
                st.subheader("Komposisi status di setiap jenis lelang")
                plot(type_chart(view), "type_chart")
                st.caption("Persentase memakai jumlah lot setiap jenis sebagai denominator. n menunjukkan ukuran kelompok; pembulatan dapat membuat jumlah label berbeda dari 100%.")

if tabs[2].open:
    with tabs[2]:
        cols = st.columns(2)
        with cols[0]:
            st.subheader("Sebaran nilai limit")
            plot(limit_chart(view), "limit_chart")
        with cols[1]:
            st.subheader("Nilai limit per kategori aset")
            plot(asset_chart(view), "asset_chart")
        st.caption("Skala nilai: Rp juta. Kotak = kuartil 25-75%, garis = median, whisker = hingga 1,5 IQR. Titik ekstrem disembunyikan tetapi tetap dihitung. Kategori aset memakai kata kunci nama lot.")

if tabs[3].open:
    with tabs[3]:
        cols = st.columns(2)
        with cols[0]:
            st.subheader("Durasi tahap proses")
            plot(duration_chart(view), "duration_chart")
        with cols[1]:
            st.subheader("Ketersediaan data")
            plot(quality_chart(view), "quality_chart")
        st.caption(f"Median penetapan ke lelang: {number(m['median_duration'], 2)} hari kalender. Durasi mempertahankan pecahan hari; SLA tidak tersedia. Nilai kosong perlu dibaca bersama status.")
        with st.expander("Definisi KPI dan pemeriksaan data"):
            st.markdown("**Jumlah lot** = baris setelah filter. **Proporsi LAKU** = lot LAKU / baris setelah filter. **Nilai limit** dan **pokok** = jumlah nilai tersedia. **Total bea** = empat komponen bea tercatat. **Durasi** = selisih timestamp / 86.400 detik; durasi negatif tidak masuk distribusi.")
            table(pd.DataFrame(diagnostics(view).items(), columns=["Pemeriksaan", "Hasil"]), "Pemeriksaan data")
            table(quality(view), "Ketersediaan data")
            st.caption("Pokok tersedia pada 240 lot LAKU pada dataset penuh. Pola data latihan ini bukan aturan umum atau bukti seluruh nilai kosong adalah kesalahan.")

if tabs[4].open:
    with tabs[4]:
        items = stories(view)
        for col, item in zip(st.columns(3), items):
            with col:
                esc = lambda v: html.escape(str(v))
                st.markdown(f'<div class="story"><h4>{esc(item["title"])}</h4><p><b>Temuan</b><br>{esc(item["finding"])}</p><p><b>Makna</b><br>{esc(item["meaning"])}</p><p><b>Tindakan</b><br>{esc(item["action"])}</p></div>', unsafe_allow_html=True)
        with st.expander("Usulan agenda sebelum rapat evaluasi berikutnya"):
            table(pd.DataFrame([{"Penanggung jawab": s["owner"], "Tindak lanjut": s["action"],
                                 "Hasil yang diharapkan": s["deliverable"]} for s in items]), "Agenda tindak lanjut")

if tabs[5].open:
    with tabs[5]:
        st.subheader("Detail lot pada cakupan terpilih")
        detail = safe_detail(view)
        search = st.text_input("Cari kode lot", placeholder="Contoh: DDTOTL", key="cari_lot")
        if search:
            detail = detail[detail.kode_lot.astype(str).str.contains(search.strip(), case=False, regex=False)]
        st.caption(f"{number(len(detail))} baris. Pencarian hanya membatasi tabel dan unduhan; KPI dan grafik mengikuti filter sidebar.")
        pages = max(1, (len(detail) + 49) // 50)
        if st.session_state.get("detail_halaman", 1) > pages:
            st.session_state.detail_halaman = 1
        page = st.selectbox("Halaman detail · 50 baris per halaman", range(1, pages + 1),
                            format_func=lambda n: f"{n} dari {pages}", key="detail_halaman", width=220)
        table(detail.iloc[(page - 1) * 50:page * 50], "Detail lot", {
            "nilai_limit": "Nilai limit (Rp)", "pokok_lelang": "Pokok lelang (Rp)",
            "total_bea_tercatat": "Bea tercatat (Rp)", "hari_penetapan_lelang": "Penetapan-lelang (hari)",
            "tgl_lelang": "Tanggal lelang"})
        st.download_button("Unduh detail CSV", detail.to_csv(index=False).encode("utf-8-sig"),
                           file_name="detail_lelang_terfilter.csv", mime="text/csv", on_click="ignore")
        st.caption("CSV memuat seluruh hasil filter dan pencarian, melampaui 50 baris yang tampil pada halaman ini. Nama pribadi, NIP, nama debitur, dan kontak tidak disertakan.")
