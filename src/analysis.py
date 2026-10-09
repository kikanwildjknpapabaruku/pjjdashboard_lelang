"""Pembacaan, validasi, agregasi, dan narasi analisis. Sumber tidak diubah."""
from pathlib import Path
import math
import re
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "Dummy_Kinerja_Lelang.xlsx"
SHEET = "RAW Kinerja Lelang"
MISSING_STATUS = "Belum Ada Status"
DATE_COLUMNS = ["tgl_penetapan", "tgl_penayangan", "tgl_lelang", "tanggal_pelunasan"]
FEES = ["bea_permohonan", "bea_batal", "bea_lelang_pembeli", "bea_lelang_penjual"]
STATUS_COLORS = {
    "LAKU": "#008578", "WANPRESTASI": "#C25243", "BATAL": "#C58B32",
    MISSING_STATUS: "#8B95A7", "BELUM TAYANG": "#BCCBE1",
    "MULAI PENAWARAN": "#6B94C5", "SELESAI PENAWARAN": "#536DA8", "TAP": "#9A82B6",
}
SAFE_COLUMNS = ["kanwil", "kpknl", "kode_lot", "jenis_lelang", "kategori_aset",
                "tgl_lelang", "status_tampil", "nilai_limit", "pokok_lelang",
                "total_bea_tercatat", "hari_penetapan_lelang"]


def number(value, digits=0):
    if value is None or pd.isna(value):
        return "Tidak tersedia"
    return f"{value:,.{digits}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def rupiah(value):
    if value is None or pd.isna(value):
        return "Tidak tersedia"
    if abs(value) >= 1e9:
        return f"Rp{number(value / 1e9, 2)} miliar"
    if abs(value) >= 1e6:
        return f"Rp{number(value / 1e6, 2)} juta"
    return f"Rp{number(value)}"


def category(text):
    text = re.sub(r"<[^>]+>", "", str(text)).lower()
    for keyword, label in [("tanah", "Tanah/Bangunan"),
                           ("kendaraan roda empat", "Kendaraan Roda 4"),
                           ("kendaraan roda dua", "Kendaraan Roda 2"),
                           ("barang inventaris", "Barang Inventaris")]:
        if keyword in text:
            return label
    return "Lainnya"


def load_data(path=DATA):
    frame = pd.read_excel(path, sheet_name=SHEET)
    required = set(DATE_COLUMNS + FEES + ["kanwil", "kpknl", "kode_lot", "nama_lot",
                                        "jenis_lelang", "status_lelang", "nilai_limit", "pokok_lelang"])
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Kolom sumber belum lengkap: {', '.join(sorted(missing))}")
    for col in DATE_COLUMNS:
        original = frame[col]
        frame[f"invalid_{col}"] = original.notna() & pd.to_datetime(original, errors="coerce").isna()
        frame[col] = pd.to_datetime(original, errors="coerce")
    for col in ["nilai_limit", "pokok_lelang"] + FEES:
        original = frame[col]
        frame[col] = pd.to_numeric(original, errors="coerce")
        frame[f"invalid_{col}"] = original.notna() & frame[col].isna()
    for col in ["kanwil", "kpknl", "jenis_lelang"]:
        frame[col] = frame[col].astype("string").str.strip().fillna("Tidak tersedia")
    status = frame["status_lelang"].astype("string").str.strip().str.upper().replace("", pd.NA)
    frame["status_tampil"] = status.fillna(MISSING_STATUS)
    frame["kanwil_ringkas"] = frame["kanwil"].str.replace("Kantor Wilayah DJKN ", "", regex=False)
    frame["kategori_aset"] = frame["nama_lot"].map(category)
    for label, start, end in [("hari_penetapan_tayang", "tgl_penetapan", "tgl_penayangan"),
                              ("hari_tayang_lelang", "tgl_penayangan", "tgl_lelang"),
                              ("hari_penetapan_lelang", "tgl_penetapan", "tgl_lelang")]:
        duration = (frame[end] - frame[start]).dt.total_seconds() / 86400
        frame[f"negatif_{label}"] = duration.lt(0)
        frame[label] = duration.where(duration.ge(0))
    # min_count mempertahankan NaN jika semua komponen tidak tersedia.
    frame["total_bea_tercatat"] = frame[FEES].sum(axis=1, min_count=1)
    return frame


def filter_data(frame, start=None, end=None, **choices):
    mask = pd.Series(True, index=frame.index)
    if start is not None:
        mask &= frame["tgl_lelang"].ge(pd.Timestamp(start))
    if end is not None:
        mask &= frame["tgl_lelang"].lt(pd.Timestamp(end).normalize() + pd.Timedelta(days=1))
    for col, values in choices.items():
        if values:
            mask &= frame[col].isin(values)
    return frame.loc[mask].copy()


def metrics(frame):
    n = len(frame)
    laku = int(frame.status_tampil.eq("LAKU").sum())
    missing = int(frame.status_tampil.eq(MISSING_STATUS).sum())
    return dict(lot=n, limit=frame.nilai_limit.sum(min_count=1), laku=laku,
                laku_pct=100 * laku / n if n else np.nan,
                pokok=frame.pokok_lelang.sum(min_count=1),
                bea=frame.total_bea_tercatat.sum(min_count=1),
                missing_status=missing, missing_pct=100 * missing / n if n else np.nan,
                median_limit=frame.nilai_limit.median(),
                median_duration=frame.hari_penetapan_lelang.median(),
                pokok_count=int(frame.pokok_lelang.notna().sum()))


def by_region(frame, column="kanwil_ringkas"):
    result = frame.groupby(column, observed=True).agg(
        lot=("kode_lot", "size"),
        laku=("status_tampil", lambda s: s.eq("LAKU").sum()),
        kosong=("status_tampil", lambda s: s.eq(MISSING_STATUS).sum()),
        limit=("nilai_limit", lambda s: s.sum(min_count=1)),
    ).reset_index()
    result["proporsi_laku"] = 100 * result.laku / result.lot
    result["proporsi_kosong"] = 100 * result.kosong / result.lot
    return result.sort_values(["lot", column], ascending=[False, True])


def monthly(frame, start=None, end=None):
    valid = frame.dropna(subset=["tgl_lelang"])
    if valid.empty:
        return pd.DataFrame(columns=["bulan", "lot", "hari_cakupan", "lot_per_hari", "cakupan"])
    start = pd.Timestamp(start or valid.tgl_lelang.min()).normalize()
    end = pd.Timestamp(end or valid.tgl_lelang.max()).normalize()
    counts = valid.groupby(valid.tgl_lelang.dt.to_period("M")).size()
    rows = []
    for month in pd.period_range(start, end, freq="M"):
        a, b = max(start, month.start_time.normalize()), min(end, month.end_time.normalize())
        days = (b - a).days + 1
        n = int(counts.get(month, 0))
        rows.append(dict(bulan=str(month), lot=n, hari_cakupan=days,
                         lot_per_hari=n / days, cakupan=f"{a:%d/%m} - {b:%d/%m/%Y}"))
    return pd.DataFrame(rows)


def quality(frame):
    n = len(frame)
    rows = []
    for col in ["status_lelang", "pokok_lelang", "tanggal_pelunasan"] + FEES:
        count = int(frame.status_tampil.eq(MISSING_STATUS).sum()) if col == "status_lelang" else int(frame[col].isna().sum())
        rows.append(dict(kolom=col, kosong=count, persen=100 * count / n if n else np.nan))
    return pd.DataFrame(rows)


def diagnostics(frame):
    return {
        "baris": len(frame), "kode_lot_kosong": int(frame.kode_lot.isna().sum()),
        "kode_lot_duplikat": int(frame.kode_lot.dropna().duplicated().sum()),
        "tanggal_tidak_valid": int(frame[[f"invalid_{c}" for c in DATE_COLUMNS]].sum().sum()),
        "angka_tidak_valid": int(frame[[f"invalid_{c}" for c in ["nilai_limit", "pokok_lelang"] + FEES]].sum().sum()),
        "durasi_negatif": int(frame[[c for c in frame if c.startswith("negatif_")]].any(axis=1).sum()),
        "LAKU_tanpa_pokok": int((frame.status_tampil.eq("LAKU") & frame.pokok_lelang.isna()).sum()),
        "non_LAKU_dengan_pokok": int((~frame.status_tampil.eq("LAKU") & frame.pokok_lelang.notna()).sum()),
    }


def stories(frame):
    if frame.empty:
        return []
    m = metrics(frame)
    regions = by_region(frame).sort_values(["kosong", "lot"], ascending=False)
    top = regions.iloc[0]
    eligible = frame[frame.nilai_limit.ge(0)].dropna(subset=["nilai_limit"])
    k = max(1, math.ceil(len(eligible) * .1))
    concentration = eligible.nlargest(k, "nilai_limit").nilai_limit.sum() / eligible.nilai_limit.sum() * 100 if eligible.nilai_limit.sum() > 0 else np.nan
    assets = frame.groupby("kategori_aset", observed=True).agg(lot=("kode_lot", "size"), nilai=("nilai_limit", "sum")).sort_values("nilai", ascending=False)
    asset = assets.index[0]
    result = [
        {"title": "Lengkapi status sebelum menilai outcome",
         "finding": f"{number(m['missing_status'])} dari {number(m['lot'])} lot ({number(m['missing_pct'], 1)}%) belum memiliki status. LAKU tercatat {number(m['laku'])} lot ({number(m['laku_pct'], 1)}% dari observasi terpilih).",
         "meaning": "Status proses, pembatalan, dan status kosong bercampur dalam dataset. Proporsi LAKU belum dapat ditafsirkan sebagai tingkat keberhasilan resmi.",
         "action": "Rekonsiliasi status dan tanggal pembaruan, lalu sepakati status final dan denominator bersama pemilik proses sebelum menetapkan KPI keberhasilan.",
         "owner": "Pengelola data dan pemilik proses", "deliverable": "Daftar status terverifikasi dan definisi KPI"},
        {"title": "Arahkan penelaahan wilayah pada volume dan kelengkapan",
         "finding": f"{top.kanwil_ringkas} memiliki {number(top.kosong)} status kosong dari {number(top.lot)} lot ({number(top.proporsi_kosong, 1)}%), jumlah status kosong terbesar pada cakupan terpilih; peringkat dapat seri.",
         "meaning": "Jumlah status kosong menunjukkan besarnya pekerjaan verifikasi. Perbedaan komposisi jenis lelang dan tahap proses membatasi perbandingan outcome antarwilayah.",
         "action": "Telusuri lot tanpa status pada KPKNL di wilayah tersebut dan bandingkan jenis lelang serta tahap proses sebelum menyimpulkan perbedaan kinerja.",
         "owner": "Koordinator Kanwil dan KPKNL", "deliverable": "Daftar lot untuk ditelaah dan penyebab status kosong"},
        {"title": "Prioritaskan telaah lot yang membawa nilai besar",
         "finding": f"{number(k)} lot dengan nilai limit tertinggi (sekitar 10% lot bernilai valid) memuat {number(concentration, 1)}% total nilai limit valid. {asset} memiliki nilai limit agregat terbesar, {rupiah(assets.iloc[0].nilai)}.",
         "meaning": "Volume lot saja tidak menggambarkan konsentrasi nilai. Nilai limit merupakan nilai penawaran minimum pada data latihan dan tidak sama dengan penerimaan yang telah terealisasi.",
         "action": "Susun daftar lot bernilai besar untuk memeriksa kelengkapan dokumen, jadwal, dan status. Gunakan nilai pokok tercatat secara terpisah saat membahas realisasi.",
         "owner": "Tim analitik dan penanggung jawab lot", "deliverable": "Daftar prioritas berdasarkan nilai dan kelengkapan"},
    ]
    if m["missing_status"] == 0:
        result[0].update(
            title="Konfirmasi denominator sebelum menilai outcome",
            finding=f"Seluruh {number(m['lot'])} lot terpilih memiliki label status. LAKU tercatat {number(m['laku'])} lot ({number(m['laku_pct'], 1)}% dari observasi terpilih).",
            meaning="Kelengkapan label pada subset ini belum menentukan populasi yang memenuhi syarat untuk KPI keberhasilan. Filter status juga dapat mengubah denominator.",
            action="Konfirmasi status final, tanggal pembaruan, dan populasi yang memenuhi syarat bersama pemilik proses sebelum menetapkan tingkat keberhasilan resmi.")
        result[1].update(
            title="Telaah komposisi wilayah sebelum membandingkan outcome",
            finding=f"{top.kanwil_ringkas} memiliki volume terbesar pada cakupan terpilih: {number(top.lot)} lot dengan {number(top.laku)} LAKU ({number(top.proporsi_laku, 1)}%); peringkat dapat seri. Tidak ada status kosong pada cakupan ini.",
            meaning="Perbedaan volume, jenis lelang, dan tahap proses membatasi pembandingan proporsi LAKU antarwilayah.",
            action="Bandingkan jenis lelang dan tahap proses pada KPKNL di wilayah tersebut, lalu pastikan populasi pembanding dan definisi outcome setara.",
            deliverable="Perbandingan unit dengan populasi dan definisi yang disepakati")
    return result


def safe_detail(frame):
    """Hanya kolom operasional yang relevan, tanpa nama pribadi, NIP, atau debitur."""
    return frame[SAFE_COLUMNS].sort_values(["tgl_lelang", "kode_lot"]).reset_index(drop=True)
