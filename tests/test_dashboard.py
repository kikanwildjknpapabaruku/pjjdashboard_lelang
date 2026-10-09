"""Uji aplikasi nyata melalui Streamlit AppTest."""
import sys
import json
import unittest
from datetime import date
from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from analysis import filter_data, load_data


class DashboardTests(unittest.TestCase):
    def test_tabs_theme_and_detail_keep_filter_scope(self):
        app = AppTest.from_file(str(ROOT / "src" / "app.py"), default_timeout=60).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual([tab.label for tab in app.tabs],
                         ["Ringkasan", "Wilayah", "Aset", "Proses & Data", "Tindak Lanjut", "Detail Lot"])
        app.multiselect(key="kanwil").set_value(["Banten"]).run()
        light_color = json.loads(app.get("plotly_chart")[0].proto.spec)["layout"]["font"]["color"]
        app.radio(key="tampilan").set_value("Dark").run()
        self.assertEqual(app.metric[0].value, "221")
        dark_color = json.loads(app.get("plotly_chart")[0].proto.spec)["layout"]["font"]["color"]
        self.assertNotEqual(light_color, dark_color)
        for page, count in [("Wilayah", 1), ("Aset", 2), ("Proses & Data", 2), ("Tindak Lanjut", 0)]:
            app.session_state["halaman"] = page
            app.run()
            self.assertEqual(len(app.exception), 0, page)
            self.assertEqual(len(app.get("plotly_chart")), count, page)
            self.assertEqual(app.radio(key="tampilan").value, "Dark")
            self.assertEqual(app.multiselect(key="kanwil").value, ["Banten"])
            if page == "Wilayah":
                for region_view in ["KPKNL", "Jenis Lelang"]:
                    # AppTest belum memiliki aksi klik tab; state tab diatur
                    # pada setiap run. Retensi klik antartab juga diperiksa di browser.
                    app.session_state["halaman"] = "Wilayah"
                    app.session_state["wilayah_view"] = region_view
                    app.run()
                    self.assertEqual(len(app.exception), 0, region_view)
                    self.assertEqual(len(app.get("plotly_chart")), 1)
        app.session_state["halaman"] = "Detail Lot"
        app.run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.selectbox(key="detail_halaman").options, ["1 dari 5", "2 dari 5", "3 dari 5", "4 dari 5", "5 dari 5"])
        app.selectbox(key="detail_halaman").set_value(5)
        app.session_state["halaman"] = "Detail Lot"
        app.run()
        code = str(load_data().query("kanwil_ringkas == 'Banten'").iloc[0].kode_lot)
        app.text_input(key="cari_lot").set_value(code)
        app.session_state["halaman"] = "Detail Lot"
        app.run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.selectbox(key="detail_halaman").value, 1)
        self.assertTrue(any("1 baris." in caption.value for caption in app.caption))
        app.radio(key="tampilan").set_value("Light")
        app.session_state["halaman"] = "Detail Lot"
        app.run()
        self.assertEqual(app.session_state["halaman"], "Detail Lot")
        self.assertEqual(app.multiselect(key="kanwil").value, ["Banten"])
        app.text_input(key="cari_lot").set_value("TIDAK-ADA-KODE-INI")
        app.session_state["halaman"] = "Detail Lot"
        app.run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any("Tidak ada baris" in element.proto.body for element in app.get("html")))
        app.session_state["halaman"] = "Ringkasan"
        app.run()
        self.assertEqual(app.metric[0].value, "221")

    def test_overview_cascade_filters_empty_state_and_reset(self):
        app = AppTest.from_file(str(ROOT / "src" / "app.py"), default_timeout=60).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.metric[0].value, "2.000")
        self.assertEqual(app.metric[2].value, "240")
        app.multiselect(key="kanwil").set_value(["Banten"]).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.metric[0].value, "221")
        app.multiselect(key="kpknl").set_value(["KPKNL Serang"]).run()
        self.assertEqual(app.metric[0].value, "76")
        app.multiselect(key="kanwil").set_value(["Aceh"]).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.metric[0].value, "172")
        self.assertEqual(app.multiselect(key="kpknl").value, [])
        app.multiselect(key="status").set_value(["BATAL"]).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.metric[3].value, "Tidak tersedia")
        app.button[0].click().run()
        self.assertEqual(app.metric[0].value, "2.000")
        app.multiselect(key="kanwil").set_value(["Aceh"]).run()
        app.multiselect(key="status").set_value(["LAKU"]).run()
        df = load_data()
        day = next(d.date() for d in __import__('pandas').date_range("2026-06-04", "2026-08-25")
                   if filter_data(df, d.date(), d.date(), kanwil_ringkas=["Aceh"], status_tampil=["LAKU"]).empty)
        app.date_input(key="tanggal").set_value((day, day)).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.metric), 0)
        self.assertTrue(any("Tidak ada lot" in w.value for w in app.warning))
        app.button[0].click().run()
        self.assertEqual(app.metric[0].value, "2.000")


if __name__ == "__main__":
    unittest.main()
