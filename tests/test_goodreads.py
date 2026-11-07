import unittest

import pandas as pd

from src.goodreads import goodreads_quality_audit, prepare_goodreads_frame


class PrepareGoodreadsFrameTests(unittest.TestCase):
    def setUp(self):
        self.raw = pd.DataFrame(
            {
                "title": ["Libro A", "Libro B", "Libro A", "", "Libro C"],
                "first_author": [
                    ["Ana", "Luis"],
                    "Bea",
                    ["Ana", "Luis"],
                    "Cris",
                    "Dani",
                ],
                "pages": [120, None, 120, 80, "no disponible"],
                "average_rating": [4.1, 4.8, 4.1, 4.2, 4.2],
                "publisher": ["Editorial", None, "Editorial", "Otra", "Otra"],
            }
        )

    def test_keeps_optional_missing_values_and_coerces_invalid_numbers(self):
        frame = prepare_goodreads_frame(self.raw)

        self.assertEqual(len(frame), 4)
        self.assertTrue(pd.isna(frame.loc[1, "paginas"]))
        self.assertTrue(pd.isna(frame.loc[3, "paginas"]))
        self.assertEqual(frame.loc[0, "autor"], "Ana, Luis")
        self.assertEqual(frame.loc[0, "texto"], "Libro A Ana, Luis")
        self.assertTrue(pd.isna(frame.loc[1, "editorial"]))

    def test_can_remove_duplicate_book_text(self):
        frame = prepare_goodreads_frame(self.raw, deduplicate_text=True)

        self.assertEqual(len(frame), 3)
        self.assertEqual(frame["texto"].nunique(), len(frame))

    def test_filters_ratings_outside_the_selected_range(self):
        raw = self.raw.copy()
        raw.loc[0, "average_rating"] = 5.1
        frame = prepare_goodreads_frame(raw, maximum_rating=4.9)

        self.assertNotIn(5.1, frame["calificacion"].values)

    def test_rejects_missing_required_columns(self):
        with self.assertRaisesRegex(KeyError, "average_rating"):
            prepare_goodreads_frame(self.raw.drop(columns="average_rating"))

    def test_rejects_invalid_rating_bounds(self):
        with self.assertRaises(ValueError):
            prepare_goodreads_frame(self.raw, minimum_rating=5.1)


class GoodreadsQualityAuditTests(unittest.TestCase):
    def test_reports_missing_values_outliers_and_duplicates_without_mutation(self):
        raw = pd.DataFrame(
            {
                "title": ["A", "B", "A", "D", "E"],
                "first_author": ["X", "Y", "X", "W", "V"],
                "pages": [10, 20, 30, 40, 100_000],
                "average_rating": [4.0, 4.1, 4.2, None, 5.1],
            }
        )
        original = raw.copy(deep=True)

        audit = goodreads_quality_audit(raw).set_index("indicador")["valor"]

        self.assertEqual(audit["Filas originales"], 5)
        self.assertEqual(audit["Calificaciones nulas o no numéricas"], 1)
        self.assertEqual(audit["Calificaciones fuera de [0, 5]"], 1)
        self.assertEqual(audit["Textos título+autor repetidos"], 1)
        self.assertEqual(audit["Páginas positivas sobre el percentil 99"], 1)
        pd.testing.assert_frame_equal(raw, original)


if __name__ == "__main__":
    unittest.main()
