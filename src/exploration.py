"""Hasil eksplorasi yang dapat dibuat ulang: HTML offline, PNG, CSV, dan JSON."""
import html
import json
import os
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import plotly.io as pio
from analysis import ROOT, by_region, diagnostics, load_data, metrics, monthly, number, quality, rupiah, safe_detail, stories
from charts import all_charts

OUTPUT = ROOT / "output"
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "tmp" / "matplotlib"))
CONFIG = dict(displaylogo=False, responsive=True, toImageButtonOptions={"format": "png", "scale": 2})


def overview(frame, target):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    from matplotlib.patches import FancyBboxPatch
    from analysis import STATUS_COLORS

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.spines.left": False, "axes.spines.bottom": False,
                         "text.color": "#182C49", "axes.labelcolor": "#64748B",
                         "xtick.color": "#64748B", "ytick.color": "#182C49"})
    fig = plt.figure(figsize=(16, 11.8), facecolor="#F5F7FA", dpi=150)
    fig.text(.05, .963, "ANALITIK ASET DAN LELANG", color="#008578", size=11, weight="bold")
    fig.text(.05, .918, "Kinerja Lelang", size=30, weight="bold")
    start, end = frame.tgl_lelang.min(), frame.tgl_lelang.max()
    fig.text(.05, .887, f"{start:%d/%m/%Y} - {end:%d/%m/%Y}   |   {number(len(frame))} lot   |   {frame.kanwil.nunique()} Kanwil   |   {frame.kpknl.nunique()} KPKNL", size=11, color="#64748B")
    m = metrics(frame)
    cards = [("Jumlah lot", number(m['lot'])), ("Total nilai limit", rupiah(m['limit'])),
             ("LAKU dari observasi", f"{number(m['laku'])} ({number(m['laku_pct'],1)}%)"),
             ("Pokok tercatat", rupiah(m['pokok'])), ("Total bea tercatat", rupiah(m['bea']))]
    for i, (label, value) in enumerate(cards):
        x = .05 + i * .183
        box = FancyBboxPatch((x, .788), .173, .075, boxstyle="round,pad=0.006,rounding_size=0.008", transform=fig.transFigure,
                             facecolor="white", edgecolor="#DFE6EF", linewidth=.7, zorder=-1)
        fig.patches.append(box)
        fig.text(x + .009, .839, label, size=10, color="#64748B")
        fig.text(x + .009, .808, value, size=14, weight="bold")
    fig.text(.05, .765, "Proporsi LAKU bukan tingkat keberhasilan resmi. Angka keuangan hanya menjumlahkan nilai tercatat.", size=9, color="#64748B")
    grid = fig.add_gridspec(2, 2, left=.19, right=.955, top=.70, bottom=.12, wspace=.55, hspace=.58)
    ax = fig.add_subplot(grid[0, 0], facecolor="#F5F7FA")
    counts = frame.status_tampil.value_counts().sort_values()
    ax.barh(counts.index, counts.values, color=[STATUS_COLORS.get(s, "#5378A8") for s in counts.index], height=.64)
    for i, n in enumerate(counts):
        ax.text(n + 4, i, f"{n} ({number(n/len(frame)*100,1)}%)", va="center", size=9)
    ax.set_xlim(0, counts.max()*1.48)
    ax.set_title("01  Komposisi status", loc="left", weight="bold", pad=17, size=13)
    ax.set_xlabel("Jumlah lot")
    ax.tick_params(axis="both", length=0, labelsize=9)

    ax = fig.add_subplot(grid[0, 1], facecolor="#F5F7FA")
    periods = frame.tgl_lelang.dt.to_period("W-SUN")
    weeks = frame.groupby(periods).size()
    dates = weeks.index.start_time
    ax.plot(dates, weeks, color="#008578", linewidth=2.6, marker="o", markersize=4)
    ax.fill_between(dates, weeks, alpha=.07, color="#008578")
    ax.set_title("02  Volume lelang mingguan", loc="left", weight="bold", pad=17, size=13)
    import matplotlib.dates as mdates
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax.set_ylabel("Jumlah lot")
    ax.grid(axis="y", color="#E1E7EF", linewidth=.7)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)
    ax.text(0, -.27, "Minggu pertama/terakhir tercakup sebagian.", transform=ax.transAxes, size=9, color="#64748B")

    ax = fig.add_subplot(grid[1, 0], facecolor="#F5F7FA")
    region = by_region(frame).iloc[::-1]
    short = region.kanwil_ringkas.replace({"Sulawesi Selatan Tenggara Barat": "Sulsel, Sultra, Sulbar", "Kalimantan Selatan Tengah": "Kalsel, Kalteng"})
    ax.barh(short, region.lot, color="#BDD2E4", height=.65)
    ax.barh(short, region.kosong, color="#8B95A7", height=.65, label="Tanpa status (bagian dari total)")
    for i, row in enumerate(region.itertuples()):
        ax.text(row.lot + 3, i, str(row.lot), va="center", size=9)
    ax.set_xlim(0, region.lot.max()*1.19)
    ax.set_title("03  Volume dan status kosong per Kanwil", loc="left", weight="bold", pad=17, size=13)
    ax.set_xlabel("Jumlah lot")
    ax.tick_params(length=0, labelsize=9)
    ax.legend(loc="lower left", bbox_to_anchor=(-.02, -.30), frameon=False, fontsize=8)

    ax = fig.add_subplot(grid[1, 1], facecolor="#F5F7FA")
    months = monthly(frame)
    x = np.arange(len(months))
    ax.bar(x, months.lot_per_hari, color=["#008578" if v == months.lot_per_hari.max() else "#BDD2E4" for v in months.lot_per_hari], width=.53)
    for i, row in enumerate(months.itertuples()):
        ax.text(i, row.lot_per_hari + .7, number(row.lot_per_hari, 2), ha="center", weight="bold", size=12)
    ax.set_xticks(x, [f"{a}\n{int(b)} hari cakupan" for a,b in zip(months.bulan, months.hari_cakupan)])
    ax.set_ylim(0, months.lot_per_hari.max()*1.22)
    ax.set_title("04  Volume per hari dalam cakupan", loc="left", weight="bold", pad=17, size=13)
    ax.set_ylabel("Lot per hari kalender")
    ax.grid(axis="y", color="#E1E7EF", linewidth=.7)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)
    fig.text(.05, .037, "Sumber: Dummy_Kinerja_Lelang.xlsx. Data latihan; tanggal pembaruan status dan SLA tidak tersedia.", size=9, color="#64748B")
    fig.savefig(target, facecolor=fig.get_facecolor(), dpi=150)
    plt.close(fig)


def export_html(frame, chart_items):
    esc = html.escape
    m = metrics(frame)
    cards = [("Jumlah lot", number(m['lot']), "observasi dalam dataset"),
             ("Total nilai limit", rupiah(m['limit']), "nilai limit tercatat"),
             ("Lot LAKU", number(m['laku']), f"{number(m['laku_pct'],1)}% dari seluruh observasi"),
             ("Pokok lelang tercatat", rupiah(m['pokok']), f"tersedia pada {m['pokok_count']} lot"),
             ("Total bea tercatat", rupiah(m['bea']), "empat komponen bea")]
    card_html = ''.join(f'<div class="kpi"><span>{esc(a)}</span><strong>{esc(b)}</strong><small>{esc(c)}</small></div>' for a,b,c in cards)
    chart_html = []
    for i, (key, title, caption, fig) in enumerate(chart_items):
        plot = pio.to_html(fig, full_html=False, include_plotlyjs=True if i == 0 else False, config=CONFIG, div_id=key)
        full = " full" if i in [2,3,4] else ""
        chart_html.append(f'<article class="panel{full}"><h3>{esc(title)}</h3>{plot}<p class="caption">{esc(caption)}</p></article>')
    narratives = ''.join(f'<article class="story"><div class="num">0{i+1}</div><h3>{esc(s["title"])}</h3><b>Temuan</b><p>{esc(s["finding"])}</p><b>Makna</b><p>{esc(s["meaning"])}</p><b>Tindakan</b><p>{esc(s["action"])}</p><p class="caption">{esc(s["owner"])}<br>Hasil: {esc(s["deliverable"])}</p></article>' for i,s in enumerate(stories(frame)))
    detail = safe_detail(frame).copy()
    detail["tgl_lelang"] = detail.tgl_lelang.dt.strftime("%d/%m/%Y %H:%M")
    for col in ["nilai_limit", "pokok_lelang", "total_bea_tercatat"]:
        detail[col] = detail[col].map(lambda x: "" if pd.isna(x) else number(x))
    detail["hari_penetapan_lelang"] = detail.hari_penetapan_lelang.map(lambda x: number(x,2))
    detail_table = detail.to_html(index=False, border=0, table_id="detail-table", escape=True)
    monthly_table = monthly(frame).to_html(index=False, border=0, float_format=lambda v:number(v,2))
    template = '''<!doctype html><html lang="id"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Kinerja Lelang - Studi Kasus</title>
<style>
:root{--ink:#182C49;--muted:#64748B;--teal:#008578;--line:#E1E7EF}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#F5F7FA;color:var(--ink);font:15px/1.6 Arial,sans-serif}a{color:var(--teal)}header{background:white;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:9}nav{max-width:1420px;margin:auto;padding:14px 30px;display:flex;align-items:center;gap:25px}nav strong{margin-right:auto;font-size:14px}nav a{text-decoration:none;font-size:13px;color:var(--muted)}main{max-width:1420px;margin:auto;padding:36px 30px 55px}.eyebrow{font-size:11px;letter-spacing:.19em;color:var(--teal);font-weight:700}h1{font-size:42px;line-height:1.18;margin:10px 0 14px;letter-spacing:-.04em}h2{font-size:24px;margin:38px 0 18px;letter-spacing:-.025em}h3{font-size:17px;line-height:1.45;margin:0 0 12px}p{margin:8px 0 16px}.scope{color:var(--muted);margin-bottom:18px}.note{background:#E8F2EF;border-left:3px solid var(--teal);padding:13px 17px;font-size:13px;color:#315B56;border-radius:0 7px 7px 0}.kpis{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px;margin:24px 0}.kpi{background:white;border:1px solid var(--line);border-radius:12px;padding:18px 16px}.kpi span{display:block;color:var(--muted);font-size:12px}.kpi strong{display:block;font-size:23px;letter-spacing:-.04em;margin:7px 0}.kpi small{display:block;color:var(--muted);font-size:11px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.panel{background:white;border:1px solid var(--line);border-radius:12px;padding:22px 22px 14px;min-width:0;overflow:hidden}.panel.full{grid-column:1/-1}.caption{font-size:12px;color:var(--muted);line-height:1.65}.stories{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}.story{background:white;border:1px solid var(--line);border-top:4px solid var(--teal);border-radius:10px;padding:23px}.story p{font-size:13px;color:#44536A}.story b{font-size:12px}.num{font-size:12px;color:var(--teal);font-weight:bold;margin-bottom:12px}.table-wrap{overflow:auto;max-height:520px;background:white;border:1px solid var(--line);border-radius:10px}table{border-collapse:collapse;width:100%;font-size:12px;white-space:nowrap}th{position:sticky;top:0;background:#EAF0F6;text-align:left;padding:12px 15px;color:var(--ink)}td{padding:10px 15px;border-top:1px solid #EDF1F5}tbody tr:hover{background:#F4F8FA}input{padding:12px 15px;border:1px solid #CBD5E1;border-radius:7px;font:14px Arial;width:360px;max-width:100%;margin:0 0 15px}.toolbar{display:flex;align-items:center;gap:20px;flex-wrap:wrap}.toolbar a{font-size:13px}details{margin:18px 0}summary{cursor:pointer;font-size:13px;color:var(--teal)}footer{margin-top:35px;padding-top:22px;border-top:1px solid var(--line);font-size:12px;color:var(--muted)}section{scroll-margin-top:75px}@media(max-width:1000px){.kpis{grid-template-columns:repeat(3,1fr)}.stories{grid-template-columns:1fr}.grid{grid-template-columns:1fr}}@media(max-width:600px){main{padding:25px 16px}nav{padding:12px 16px;gap:14px}nav strong{font-size:11px}nav a{font-size:11px}.kpis{grid-template-columns:1fr 1fr}h1{font-size:34px}.panel{padding:16px 10px}.kpi strong{font-size:19px}}
</style></head><body><header><nav><strong>ANALITIK ASET DAN LELANG</strong><a href="#overview">Gambaran umum</a><a href="#diagnosis">Diagnosis</a><a href="#action">Tindak lanjut</a></nav></header><main>
<div class="eyebrow">STUDI KASUS VISUALISASI DATA DENGAN PYTHON</div><h1>Kinerja Lelang</h1><p class="scope">4 Juni - 25 Agustus 2026 · 2.000 lot · 10 Kanwil · 37 KPKNL</p>
<p>Ringkasan volume, status, dan nilai untuk membantu rapat evaluasi.</p><div class="note">Data latihan. Proporsi LAKU menggunakan seluruh observasi sebagai denominator dan bukan tingkat keberhasilan resmi. HTML ini mencakup seluruh dataset; gunakan aplikasi Streamlit untuk filter lintas grafik.</div>
<section id="overview"><h2>01 &nbsp; Gambaran umum</h2><div class="kpis">__CARDS__</div><div class="grid">__OVERVIEW__</div>
<details><summary>Cakupan bulanan dan volume per hari kalender</summary><p class="caption">Hari cakupan adalah hari kalender dalam jendela data, termasuk hari tanpa lot. Rasio ini bukan produktivitas hari kerja. Juni dan Agustus tidak tercakup penuh.</p><div class="table-wrap">__MONTHS__</div></details></section>
<section id="diagnosis"><h2>02 &nbsp; Diagnosis wilayah dan portofolio</h2><div class="grid">__DIAGNOSIS__</div>
<details><summary>Definisi KPI dan pemeriksaan data</summary><p class="caption">Jumlah lot = jumlah observasi. Nilai limit dan pokok = jumlah nilai tersedia. Bea = jumlah bea permohonan, bea batal, bea pembeli, dan bea penjual yang tercatat. Nilai kosong tidak diisi nol; bila semua nilai kosong, agregat ditandai tidak tersedia. Durasi negatif ditandai dan dikeluarkan dari distribusi. Kategori aset memakai kata kunci nama lot.</p><pre>__DIAGNOSTICS__</pre><p class="caption">Pokok tersedia pada 240 lot LAKU; 1.760 nilai kosong terkait status lain pada data latihan ini. Tanggal pembaruan status dan SLA tidak tersedia.</p></details></section>
<section id="action"><h2>03 &nbsp; Temuan dan tindak lanjut</h2><div class="stories">__STORIES__</div><p class="caption">Penanggung jawab dan hasil di atas merupakan usulan agenda sebelum rapat evaluasi berikutnya.</p></section>
<section><h2>Detail lot</h2><p class="caption">Kolom operasional tanpa nama pribadi, NIP, nama debitur, atau kontak. Pencarian hanya membatasi tabel.</p><div class="toolbar"><input id="search" type="search" placeholder="Cari kode lot, wilayah, jenis, atau status" aria-label="Cari detail lot"><a href="detail_lelang.csv" download>Unduh seluruh detail CSV</a><span id="row-count" class="caption">2.000 baris</span></div><div class="table-wrap">__DETAIL__</div></section>
<footer>Sumber: Dummy_Kinerja_Lelang.xlsx, sheet RAW Kinerja Lelang (2.000 baris, 30 variabel asli). Pedoman: Studi_Kasus_Visualisasi_Data_dengan_Python_Aset_dan_Lelang.pdf. Grafik mendukung hover, zoom, klik legenda, dan unduh PNG. Seluruh pustaka grafik tertanam dalam file; tidak memerlukan koneksi internet.</footer>
<noscript><p>Aktifkan JavaScript untuk menampilkan grafik dan pencarian.</p></noscript></main><script>
const rows = [...document.querySelectorAll('#detail-table tbody tr')];
document.getElementById('search').addEventListener('input', e => {const q=e.target.value.toLowerCase().trim();let n=0;for(const row of rows){const match=row.textContent.toLowerCase().includes(q);row.hidden=!match;if(match)n++;}document.getElementById('row-count').textContent=n.toLocaleString('id-ID')+' baris';});
</script></body></html>'''
    scope = f"{frame.tgl_lelang.min():%d/%m/%Y} - {frame.tgl_lelang.max():%d/%m/%Y} · {number(len(frame))} lot · {frame.kanwil.nunique()} Kanwil · {frame.kpknl.nunique()} KPKNL"
    template = template.replace("4 Juni - 25 Agustus 2026 · 2.000 lot · 10 Kanwil · 37 KPKNL", esc(scope))
    template = template.replace('id="row-count" class="caption">2.000 baris', f'id="row-count" class="caption">{number(len(frame))} baris')
    replacements = {"__CARDS__": card_html, "__OVERVIEW__": ''.join(chart_html[:2]),
                    "__DIAGNOSIS__": ''.join(chart_html[2:]), "__STORIES__": narratives,
                    "__DETAIL__": detail_table, "__MONTHS__": monthly_table,
                    "__DIAGNOSTICS__": esc(json.dumps(diagnostics(frame), ensure_ascii=False, indent=2))}
    for key, value in replacements.items():
        template = template.replace(key, value)
    (OUTPUT / "dashboard_lelang.html").write_text(template, encoding="utf-8")


def main():
    OUTPUT.mkdir(exist_ok=True)
    image_dir = OUTPUT / "grafik"
    image_dir.mkdir(exist_ok=True)
    df = load_data()
    charts = all_charts(df)
    export_html(df, charts)
    safe_detail(df).to_csv(OUTPUT / "detail_lelang.csv", index=False, encoding="utf-8-sig")
    by_region(df).to_csv(OUTPUT / "ringkasan_kanwil.csv", index=False, encoding="utf-8-sig")
    by_region(df, "kpknl").to_csv(OUTPUT / "ringkasan_kpknl.csv", index=False, encoding="utf-8-sig")
    monthly(df).to_csv(OUTPUT / "ringkasan_bulanan.csv", index=False, encoding="utf-8-sig")
    quality(df).to_csv(OUTPUT / "ketersediaan_data.csv", index=False, encoding="utf-8-sig")
    summary = {"kpi": {k: None if pd.isna(v) else float(v) for k,v in metrics(df).items()},
               "pemeriksaan": diagnostics(df), "narasi": stories(df)}
    (OUTPUT / "ringkasan_analisis.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    overview(df, OUTPUT / "ringkasan_visual.png")
    if "--skip-chart-png" not in sys.argv:
        for key, title, caption, fig in charts:
            fig.update_layout(title=dict(text=title, font_size=20, x=.03, y=.98), margin_t=95,
                              paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF")
            fig.write_image(image_dir / f"{key}.png", width=1400, height=max(500, fig.layout.height + 80), scale=1.5)
            print(f"PNG selesai: {key}", flush=True)
    print(f"Hasil disimpan di {OUTPUT}", flush=True)


if __name__ == "__main__":
    main()
