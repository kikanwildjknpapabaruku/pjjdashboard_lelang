"""Grafik Plotly untuk aplikasi dan laporan HTML."""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from analysis import MISSING_STATUS, STATUS_COLORS, by_region, number, quality

TEAL = "#008578"
NAVY = "#182C49"
BLUE = "#5378A8"
AMBER = "#C58B32"


def style(fig, x=None, y=None, height=390):
    fig.update_layout(template="plotly_white", font=dict(family="Arial, sans-serif", size=12, color=NAVY),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      margin=dict(l=12, r=24, t=20, b=46), height=height,
                      hoverlabel=dict(bgcolor="white", font_size=13),
                      separators=",.", legend_title_text="", title=None)
    fig.update_xaxes(title=x, gridcolor="#E8EDF3", zeroline=False, automargin=True)
    fig.update_yaxes(title=y, gridcolor="#E8EDF3", zeroline=False, automargin=True)
    return fig


def status_chart(frame):
    counts = frame.status_tampil.value_counts().sort_values()
    labels = [f"{number(n)} ({number(n / len(frame) * 100, 1)}%)" for n in counts]
    fig = go.Figure(go.Bar(x=counts.values, y=counts.index, orientation="h",
                          marker_color=[STATUS_COLORS.get(s, BLUE) for s in counts.index],
                          text=labels, textposition="outside", cliponaxis=False,
                          hovertemplate="%{y}<br>%{text}<extra></extra>"))
    style(fig, "Jumlah lot", height=370)
    fig.update_xaxes(range=[0, counts.max() * 1.48])
    return fig


def trend_chart(frame, granularity="Mingguan", start=None, end=None):
    valid = frame.dropna(subset=["tgl_lelang"]).copy()
    freq = "W-SUN" if granularity == "Mingguan" else "M"
    valid["periode"] = valid.tgl_lelang.dt.to_period(freq)
    first = pd.Timestamp(start or valid.tgl_lelang.min())
    last = pd.Timestamp(end or valid.tgl_lelang.max())
    periods = pd.period_range(first, last, freq=freq)
    fig = go.Figure()
    for label, subset, color in [("Semua lot", valid, TEAL),
                                  ("LAKU", valid[valid.status_tampil.eq("LAKU")], BLUE),
                                  ("Belum Ada Status", valid[valid.status_tampil.eq(MISSING_STATUS)], "#8B95A7")]:
        counts = subset.groupby("periode", observed=True).size().reindex(periods, fill_value=0)
        windows = [f"{max(p.start_time, first).strftime('%d/%m/%Y')} - {min(p.end_time, last).strftime('%d/%m/%Y')}" for p in periods]
        fig.add_scatter(x=periods.start_time, y=counts, mode="lines+markers", name=label,
                        line=dict(color=color, width=3 if label == "Semua lot" else 2),
                        marker=dict(size=5), customdata=windows,
                        hovertemplate="%{customdata}<br>" + label + ": %{y} lot<extra></extra>")
    style(fig, "Awal periode", "Jumlah lot", 370)
    fig.update_layout(legend=dict(orientation="h", y=1.15, x=0), hovermode="x unified")
    fig.update_xaxes(tickformat="%d %b" if freq == "W-SUN" else "%b %Y")
    return fig


def region_chart(frame):
    order = by_region(frame).kanwil_ringkas.tolist()[::-1]
    temp = frame.assign(kelompok=frame.status_tampil.where(frame.status_tampil.isin(["LAKU", "WANPRESTASI", "BATAL", MISSING_STATUS]), "Status lainnya"))
    table = pd.crosstab(temp.kanwil_ringkas, temp.kelompok).reindex(order, fill_value=0)
    fig = go.Figure()
    for label, color in [("LAKU", TEAL), ("WANPRESTASI", "#C25243"), ("BATAL", AMBER),
                         (MISSING_STATUS, "#8B95A7"), ("Status lainnya", "#C3D3E6")]:
        if label in table:
            fig.add_bar(x=table[label], y=order, name=label, orientation="h", marker_color=color,
                        hovertemplate="%{y}<br>" + label + ": %{x} lot<extra></extra>")
    style(fig, "Jumlah lot", height=max(320, len(order) * 33 + 100))
    fig.update_layout(barmode="stack", legend=dict(orientation="h", y=-.20, x=0), margin_b=100)
    return fig


def type_chart(frame):
    order = frame.jenis_lelang.value_counts().index
    table = pd.crosstab(frame.jenis_lelang, frame.status_tampil).reindex(index=order, fill_value=0)
    columns = [s for s in STATUS_COLORS if s in table] + [s for s in table if s not in STATUS_COLORS]
    table = table.reindex(columns=columns)
    pct = table.div(table.sum(axis=1), axis=0) * 100
    labels = [s.replace(" ", "<br>", 1) if len(s) > 13 else s for s in columns]
    ylabels = [f"{name}<br>(n={number(int(table.loc[name].sum()))})" for name in table.index]
    fig = go.Figure(go.Heatmap(z=pct.values, x=labels, y=ylabels, customdata=table.values,
                              text=[[f"{number(v, 0)}%" for v in row] for row in pct.values],
                              texttemplate="%{text}", colorscale=[[0, "#F3F7FB"], [1, TEAL]], zmin=0,
                              zmax=max(25, float(pct.values.max())), colorbar=dict(title="% per jenis", thickness=12),
                              hovertemplate="%{y}<br>%{x}<br>%{customdata} lot (%{z:.1f}%)<extra></extra>"))
    style(fig, height=max(430, len(table) * 40 + 100))
    fig.update_yaxes(autorange="reversed", tickfont_size=11)
    fig.update_xaxes(side="top", tickfont_size=10)
    return fig


def unit_chart(frame):
    units = by_region(frame, "kpknl")
    units["nilai_miliar"] = units.limit.fillna(0).clip(lower=0) / 1e9
    fig = px.scatter(units, x="lot", y="proporsi_laku", size="nilai_miliar", color="proporsi_kosong",
                     hover_name="kpknl", color_continuous_scale=["#D9E8E5", TEAL], size_max=35,
                     custom_data=["laku", "kosong", "nilai_miliar"], labels={"proporsi_kosong": "% tanpa status"})
    fig.update_traces(marker_line=dict(width=1, color="white"),
                      hovertemplate="<b>%{hovertext}</b><br>%{x} lot<br>LAKU: %{customdata[0]} (%{y:.1f}%)<br>Tanpa status: %{customdata[1]}<br>Limit: Rp%{customdata[2]:.2f} miliar<extra></extra>")
    style(fig, "Jumlah lot per KPKNL", "Proporsi observasi berstatus LAKU (%)", 400)
    fig.update_layout(coloraxis_colorbar=dict(title="% tanpa<br>status", thickness=12))
    return fig


def limit_chart(frame):
    values = frame.nilai_limit.dropna() / 1e6
    fig = go.Figure(go.Histogram(x=values, nbinsx=30, marker_color=TEAL,
                                 hovertemplate="Limit: %{x} juta<br>%{y} lot<extra></extra>"))
    median = values.median()
    fig.add_vline(x=median, line_dash="dash", line_color=AMBER,
                  annotation_text=f"Median Rp{number(median, 1)} juta", annotation_position="top right")
    return style(fig, "Nilai limit (Rp juta)", "Jumlah lot", 360)


def asset_chart(frame):
    order = frame.groupby("kategori_aset", observed=True).nilai_limit.median().sort_values().index
    fig = px.box(frame, x="nilai_limit", y="kategori_aset", orientation="h", points=False,
                 category_orders={"kategori_aset": list(order)}, color_discrete_sequence=[TEAL])
    fig.update_traces(hovertemplate="%{y}<br>Nilai limit: Rp%{x:,.0f}<extra></extra>")
    style(fig, "Nilai limit (Rp juta)", height=360)
    fig.update_xaxes(tickvals=[0, 200e6, 400e6, 600e6, 800e6], ticktext=["0", "200", "400", "600", "800"])
    return fig


def duration_chart(frame):
    columns = {"hari_penetapan_tayang": "Penetapan ke tayang", "hari_tayang_lelang": "Tayang ke lelang",
               "hari_penetapan_lelang": "Penetapan ke lelang"}
    fig = go.Figure()
    for col, label in columns.items():
        valid = frame[col].dropna()
        fig.add_box(x=valid, name=label, orientation="h", boxpoints=False,
                    marker_color=TEAL if col == "hari_penetapan_lelang" else BLUE,
                    hovertemplate=label + "<br>%{x:.2f} hari<extra></extra>")
    style(fig, "Durasi (hari kalender, termasuk pecahan hari)", height=320)
    fig.update_layout(showlegend=False)
    return fig


def quality_chart(frame):
    table = quality(frame).sort_values("persen")
    fig = go.Figure(go.Bar(x=table.persen, y=table.kolom, orientation="h", marker_color="#8B95A7",
                          text=[f"{number(v)} / {number(len(frame))}" for v in table.kosong],
                          textposition="outside", cliponaxis=False,
                          hovertemplate="%{y}<br>Kosong: %{text} (%{x:.1f}%)<extra></extra>"))
    style(fig, "Persentase nilai kosong (%)", height=320)
    fig.update_xaxes(range=[0, 120], tickvals=[0, 25, 50, 75, 100])
    return fig


def all_charts(frame, start=None, end=None):
    return [
        ("01_status", "Komposisi status lelang", "Jumlah dan persentase menggunakan seluruh observasi pada cakupan terpilih.", status_chart(frame)),
        ("02_tren", "Volume lelang dari waktu ke waktu", "Minggu pertama dan terakhir hanya mencakup tanggal yang tersedia. LAKU dan tanpa status adalah bagian dari semua lot.", trend_chart(frame, start=start, end=end)),
        ("03_kanwil", "Volume dan komposisi status menurut Kanwil", "Status lainnya mencakup BELUM TAYANG, MULAI PENAWARAN, SELESAI PENAWARAN, TAP, dan status tambahan bila ada; kelompok ini tidak dianggap outcome final.", region_chart(frame)),
        ("04_jenis", "Komposisi status di setiap jenis lelang", "Setiap baris berjumlah 100% sebelum pembulatan. n menunjukkan denominator per jenis lelang.", type_chart(frame)),
        ("05_kpknl", "Volume, proporsi LAKU, dan nilai per KPKNL", "Ukuran lingkaran = total nilai limit. Warna = proporsi tanpa status. Proporsi LAKU bukan tingkat keberhasilan resmi.", unit_chart(frame)),
        ("06_limit", "Distribusi nilai limit", "Histogram memakai skala linear dalam Rp juta. Garis putus-putus menunjukkan median.", limit_chart(frame)),
        ("07_aset", "Nilai limit menurut kategori aset", "Kotak = kuartil 25-75%, garis tengah = median, whisker = hingga 1,5 IQR. Titik ekstrem disembunyikan untuk keterbacaan, tetap masuk perhitungan.", asset_chart(frame)),
        ("08_durasi", "Durasi setiap tahap proses", "Hari dihitung dari selisih timestamp / 86.400 detik. Ini distribusi durasi, bukan bukti bottleneck atau pelanggaran SLA.", duration_chart(frame)),
        ("09_kualitas", "Ketersediaan status dan nilai keuangan", "Nilai kosong tidak otomatis berarti nol atau kesalahan. Kesesuaian dengan tahap proses perlu diperiksa.", quality_chart(frame)),
    ]
