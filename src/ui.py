"""Warna tampilan per sesi, grafik, dan tabel baca yang mengikuti pilihan mode."""
import html
import pandas as pd
from analysis import number

PALETTES = {
    "Light": {"bg": "#F5F7FA", "panel": "#FFFFFF", "text": "#182C49",
              "muted": "#53657A", "border": "#DCE4ED", "input": "#EFF3F8",
              "accent": "#008578", "grid": "#E2E9F1", "hover": "#E7F3F0"},
    "Dark": {"bg": "#0E1525", "panel": "#172235", "text": "#E4EDF8",
             "muted": "#A8B7CC", "border": "#314059", "input": "#203047",
             "accent": "#4DD0BF", "grid": "#29384E", "hover": "#243B48"},
}


def page_css(mode):
    p = PALETTES[mode]
    variables = ";".join(f"--lelang-{key}:{value}" for key, value in p.items())
    return "<style>:root{" + variables + ";color-scheme:" + mode.lower() + "}" + """
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background:var(--lelang-bg);color:var(--lelang-text)}
    .block-container {max-width:1500px;padding-top:3.7rem;padding-bottom:2rem}
    [data-testid="stSidebar"] {background:var(--lelang-panel);border-right:1px solid var(--lelang-border)}
    [data-testid="stSidebar"] *, [data-testid="stWidgetLabel"],
    [data-testid="stMarkdownContainer"], [data-testid="stMetricLabel"] {color:var(--lelang-text)}
    [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {color:var(--lelang-muted)}
    h1,h2,h3,h4 {letter-spacing:-.025em;color:var(--lelang-text)!important}
    h1 {font-size:2rem!important;margin-bottom:.2rem!important}
    h2 {font-size:1.4rem!important;padding-top:.5rem!important}
    h3 {font-size:1.05rem!important}
    [data-testid="stMetric"] {background:var(--lelang-panel);border:1px solid var(--lelang-border);
        border-radius:12px;padding:14px 16px}
    [data-testid="stMetricValue"] {font-size:1.55rem;color:var(--lelang-text)}
    .eyebrow {font-size:11px;letter-spacing:.16em;font-weight:700;color:var(--lelang-accent);margin-bottom:4px}
    .scope {font-size:13px;color:var(--lelang-muted);margin-bottom:8px}
    .story {background:var(--lelang-panel);border:1px solid var(--lelang-border);
        border-top:3px solid var(--lelang-accent);border-radius:10px;padding:18px;height:100%}
    .story h4 {font-size:16px;margin:0 0 12px}
    .story p {font-size:13px;line-height:1.65;color:var(--lelang-muted)}
    .story b {color:var(--lelang-text)}
    [role="tablist"] {gap:4px;border-bottom:1px solid var(--lelang-border);background:var(--lelang-bg)}
    [role="tab"] {color:var(--lelang-muted);padding:10px 12px;border-radius:8px 8px 0 0}
    [role="tab"] p {font-size:14px;white-space:nowrap;color:var(--lelang-muted)}
    [role="tab"][aria-selected="true"] {color:var(--lelang-accent);background:var(--lelang-hover)}
    [role="tab"][aria-selected="true"] p {color:var(--lelang-accent);font-weight:700}
    .react-aria-SelectionIndicator {background:var(--lelang-accent)!important}
    .st-key-halaman > [role="tablist"] {position:sticky;top:3.5rem;z-index:20}
    [data-testid="stHeader"] button, [data-testid="stSidebarCollapsedControl"] button {
        color:var(--lelang-text)!important}
    [data-baseweb="select"] > div, [data-baseweb="input"], [data-baseweb="base-input"],
    [data-baseweb="textarea"], [data-testid="stMultiSelect"] [role="group"],
    [data-testid="stDateInputField"], [data-testid="stSelectbox"] button[aria-haspopup="listbox"],
    [data-testid="stTextInput"] [data-testid="stTextInputRootElement"] {
        background:var(--lelang-input)!important;color:var(--lelang-text)!important;
        border-color:var(--lelang-border)!important}
    [data-testid="stMultiSelect"] button, [data-testid="stDateInputField"] *,
    [data-testid="stSelectbox"] button {color:var(--lelang-text)!important}
    [data-testid="stMultiSelect"] [data-testid="stMultiSelectTagsContainer"] {
        background:var(--lelang-input)!important}
    input,textarea {background:transparent!important;color:var(--lelang-text)!important;
        -webkit-text-fill-color:var(--lelang-text)!important;caret-color:var(--lelang-accent)}
    input::placeholder {color:var(--lelang-muted)!important;-webkit-text-fill-color:var(--lelang-muted)!important}
    [data-baseweb="select"] span, [data-baseweb="select"] svg,
    [data-baseweb="radio"] p {color:var(--lelang-text)!important;fill:currentColor}
    [data-baseweb="tag"] {background:var(--lelang-hover)!important;color:var(--lelang-text)!important}
    [data-baseweb="popover"] > div, [role="listbox"], [role="option"],
    [data-baseweb="calendar"], [data-baseweb="calendar"] > div {
        background:var(--lelang-panel)!important;color:var(--lelang-text)!important}
    [role="option"]:hover, [role="option"][aria-selected="true"] {background:var(--lelang-hover)!important}
    [data-baseweb="calendar"] button {color:var(--lelang-text)!important}
    [data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-secondaryFormSubmit"],
    [data-testid="stDownloadButton"] button {background:var(--lelang-panel);color:var(--lelang-text);
        border-color:var(--lelang-border)}
    [data-testid="stBaseButton-secondary"]:hover, [data-testid="stDownloadButton"] button:hover {
        border-color:var(--lelang-accent);color:var(--lelang-accent)}
    [data-testid="stExpander"] details {background:var(--lelang-panel);border-color:var(--lelang-border)}
    [data-testid="stAlert"] {background:var(--lelang-hover);color:var(--lelang-text)}
    hr {border-color:var(--lelang-border)}
    .lelang-table-wrap {max-height:400px;overflow:auto;border:1px solid var(--lelang-border);
        border-radius:10px;background:var(--lelang-panel);scrollbar-color:var(--lelang-muted) var(--lelang-panel)}
    .lelang-table {border-collapse:separate;border-spacing:0;width:100%;font-size:12px;white-space:nowrap;
        color:var(--lelang-text);font-variant-numeric:tabular-nums}
    .lelang-table th {position:sticky;top:0;background:var(--lelang-input);text-align:left;
        padding:12px 14px;border-bottom:1px solid var(--lelang-border);z-index:1}
    .lelang-table td {padding:10px 14px;border-bottom:1px solid var(--lelang-border)}
    .lelang-table tbody tr:hover {background:var(--lelang-hover)}
    .lelang-table-caption {color:var(--lelang-muted);font-size:12px;padding:12px}
    @media(max-width:700px) {
        .block-container {padding-top:3.5rem}
        [role="tab"] {padding:9px 10px}
        [role="tab"] p {font-size:12px}
    }
    </style>"""


def themed_figure(fig, mode):
    """Warna data tetap bermakna sama; teks, grid, hover, dan aksen menyesuaikan."""
    p = PALETTES[mode]
    fig.update_layout(template="plotly_dark" if mode == "Dark" else "plotly_white",
                      font_color=p["text"], paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", legend_font_color=p["text"],
                      hoverlabel=dict(bgcolor=p["panel"], bordercolor=p["border"],
                                      font=dict(color=p["text"], size=13)))
    fig.update_xaxes(gridcolor=p["grid"], tickfont_color=p["text"], title_font_color=p["muted"])
    fig.update_yaxes(gridcolor=p["grid"], tickfont_color=p["text"], title_font_color=p["muted"])
    fig.update_annotations(font_color=p["text"])
    if fig.layout.coloraxis.colorbar:
        fig.update_layout(coloraxis_colorbar=dict(tickfont_color=p["text"], title_font_color=p["text"]))
    if mode == "Dark":
        colors = {"#008578": "#4DD0BF", "#5378A8": "#89ACD8", "#C58B32": "#EDB759",
                  "#C25243": "#EE8B7C", "#8B95A7": "#A3B1C5"}
        for trace in fig.data:
            if hasattr(trace, "marker"):
                color = trace.marker.color
                if isinstance(color, str):
                    trace.marker.color = colors.get(color, color)
                elif isinstance(color, (tuple, list)) and all(isinstance(c, str) for c in color):
                    trace.marker.color = [colors.get(c, c) for c in color]
            if hasattr(trace, "line") and trace.line.color:
                trace.line.color = colors.get(trace.line.color, trace.line.color)
    for trace in fig.data:
        if trace.type == "heatmap":
            trace.textfont.color = "#182C49"
            trace.colorbar.tickfont.color = p["text"]
            trace.colorbar.title.font.color = p["text"]
    return fig


def table_html(frame, label, names=None):
    """Tabel baca dengan header melekat dan HTML yang di-escape oleh Pandas."""
    display = frame.copy()
    for col in display:
        if pd.api.types.is_datetime64_any_dtype(display[col]):
            display[col] = display[col].dt.strftime("%d/%m/%Y %H:%M")
        elif pd.api.types.is_numeric_dtype(display[col]):
            digits = 2 if col.startswith("hari_") or col in ["lot_per_hari", "proporsi_laku", "proporsi_kosong", "persen"] else 0
            display[col] = display[col].map(lambda value: "—" if pd.isna(value) else number(value, digits))
    display = display.rename(columns=names or {})
    content = display.to_html(index=False, border=0, classes="lelang-table", na_rep="—", escape=True)
    if display.empty:
        content = '<p class="lelang-table-caption">Tidak ada baris yang sesuai dengan pencarian.</p>'
    return f'<div class="lelang-table-wrap" role="region" tabindex="0" aria-label="{html.escape(label, quote=True)}">{content}</div>'
