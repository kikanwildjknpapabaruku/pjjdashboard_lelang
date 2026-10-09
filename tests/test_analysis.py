"""Uji hitungan penting, semantik nilai kosong, cakupan tanggal, dan filter."""
import sys
import unittest
from datetime import date
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from analysis import (DATA, MISSING_STATUS, by_region, diagnostics, filter_data,
                      load_data, metrics, monthly, safe_detail, stories)


class AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = load_data()
        cls.raw = pd.read_excel(DATA, sheet_name="RAW Kinerja Lelang")

    def test_source_controls_and_financial_reconciliation(self):
        m = metrics(self.df)
        self.assertEqual(m["lot"], 2000)
        self.assertEqual(m["laku"], 240)
        self.assertEqual(m["missing_status"], 258)
        self.assertAlmostEqual(m["laku_pct"], 12)
        self.assertEqual(m["limit"], 410171717355)
        self.assertEqual(m["pokok"], 51258617539)
        self.assertEqual(m["bea"], 2413656000)
        independent = sum(self.raw[c].dropna().sum() for c in ["bea_permohonan", "bea_batal", "bea_lelang_pembeli", "bea_lelang_penjual"])
        self.assertEqual(m["bea"], independent)
        self.assertEqual(by_region(self.df).lot.sum(), 2000)
        self.assertEqual(by_region(self.df, "kpknl").lot.sum(), 2000)

    def test_filters_match_independent_source_selection(self):
        got = filter_data(self.df, date(2026, 7, 1), date(2026, 7, 31), kanwil_ringkas=["Banten"], status_tampil=["LAKU"])
        dates = pd.to_datetime(self.raw.tgl_lelang)
        expected = self.raw[(dates.dt.month == 7) & self.raw.kanwil.eq("Kantor Wilayah DJKN Banten") & self.raw.status_lelang.eq("LAKU")]
        self.assertEqual(set(got.kode_lot), set(expected.kode_lot))
        self.assertEqual(len(filter_data(self.df, kanwil_ringkas=["Banten"])), 221)
        self.assertEqual(len(filter_data(self.df, kpknl=["KPKNL Serang"])), 76)

    def test_end_date_includes_late_timestamp(self):
        end = date(2026, 8, 25)
        result = filter_data(self.df, end, end)
        expected = self.df[self.df.tgl_lelang.dt.date.eq(end)]
        self.assertEqual(set(result.kode_lot), set(expected.kode_lot))
        self.assertTrue(result.tgl_lelang.dt.hour.gt(0).any())

    def test_missing_pokok_is_not_reported_as_zero(self):
        result = filter_data(self.df, status_tampil=["BATAL"])
        m = metrics(result)
        self.assertTrue(pd.isna(m["pokok"]))
        self.assertEqual(m["laku"], 0)
        self.assertTrue(m["bea"] > 0)
        self.assertEqual(len(stories(result)), 3)

    def test_monthly_coverage_and_partial_months(self):
        result = monthly(self.df)
        self.assertEqual(result.lot.tolist(), [557, 988, 455])
        self.assertEqual(result.hari_cakupan.tolist(), [27, 31, 25])
        self.assertAlmostEqual(result.lot_per_hari.iloc[1], 988/31)
        single_day = filter_data(self.df, date(2026, 6, 4), date(2026, 6, 4))
        self.assertEqual(monthly(single_day, date(2026, 6, 4), date(2026, 6, 4)).hari_cakupan.iloc[0], 1)

    def test_empty_selection_and_privacy(self):
        result = filter_data(self.df, kanwil_ringkas=["Tidak ada wilayah ini"])
        self.assertEqual(len(result), 0)
        self.assertEqual(stories(result), [])
        self.assertEqual(metrics(result)["lot"], 0)
        safe = safe_detail(self.df)
        private = {"nama_pelelang", "nip_pelelang", "nama_debitur", "nama_pic", "nama_pemohon", "no_surat_permohonan"}
        self.assertFalse(private.intersection(safe.columns))

    def test_duration_uses_fractional_days(self):
        sample = self.df.iloc[0]
        expected = (sample.tgl_lelang - sample.tgl_penetapan).total_seconds()/86400
        self.assertAlmostEqual(sample.hari_penetapan_lelang, expected)
        self.assertTrue((self.df.hari_penetapan_lelang % 1 != 0).any())
        checks = diagnostics(self.df)
        for key in ["kode_lot_duplikat", "kode_lot_kosong", "tanggal_tidak_valid", "angka_tidak_valid", "durasi_negatif", "LAKU_tanpa_pokok", "non_LAKU_dengan_pokok"]:
            self.assertEqual(checks[key], 0, key)


if __name__ == "__main__":
    unittest.main()
