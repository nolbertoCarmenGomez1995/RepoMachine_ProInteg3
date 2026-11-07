import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from src.actividad3_goodreads import (
    build_cluster_profile,
    fit_and_evaluate,
    prepare_clustering_data,
    run_analysis,
)


def make_books(rows=180):
    return pd.DataFrame(
        {
            "title": [f"Libro {i}" for i in range(rows)],
            "first_author": [f"Autor {i}" for i in range(rows)],
            "pages": [30 + (i * 17) % 500 for i in range(rows)],
            "average_rating": [3.6 + (i % 14) / 10 for i in range(rows)],
            "ratings_count": [10 ** (i % 6) for i in range(rows)],
            "reviews_count": [i * 3 for i in range(rows)],
            "publisher": [f"Editorial {i % 4}" for i in range(rows)],
            "language": ["English" if i % 3 else "Spanish" for i in range(rows)],
            "is_part_of_series": [i % 2 == 0 for i in range(rows)],
        }
    )


class PrepareClusteringDataTests(unittest.TestCase):
    def test_removes_invalid_pages_and_exact_duplicates(self):
        raw = make_books()
        raw.loc[0, "pages"] = 0
        raw.loc[1, "pages"] = 100_000
        raw = pd.concat([raw, raw.iloc[[2]]], ignore_index=True)

        books, counts = prepare_clustering_data(raw)

        self.assertEqual(counts["raw_rows"], len(raw))
        self.assertEqual(counts["exact_duplicates_removed"], 1)
        self.assertEqual(counts["invalid_pages_removed"], 2)
        self.assertTrue(books["paginas"].between(20, counts["pages_upper_fence"]).all())
        self.assertNotIn("calificacion", {"log1p_cantidad_calificaciones"})

    def test_rejects_missing_required_dataset_fields(self):
        with self.assertRaisesRegex(KeyError, "average_rating"):
            prepare_clustering_data(make_books().drop(columns="average_rating"))


class KMeansEvaluationTests(unittest.TestCase):
    def test_selects_clusters_and_evaluates_only_on_validation_sample(self):
        books, _ = prepare_clustering_data(make_books())

        result = fit_and_evaluate(books, sample_size=120, validation_size=30)

        self.assertIn(result["metrics"]["best_k"], range(2, 7))
        self.assertEqual(result["metrics"]["validation_rows"], 30)
        self.assertEqual(len(result["books"]), len(books))
        self.assertEqual(result["books"]["segmento"].nunique(), result["metrics"]["best_k"])
        self.assertTrue(np.isfinite(result["metrics"]["silhouette"]))

    def test_profile_includes_business_context(self):
        books, _ = prepare_clustering_data(make_books())
        result = fit_and_evaluate(books, sample_size=120, validation_size=30)

        profile = build_cluster_profile(result["books"])

        self.assertIn("editoriales_top", profile.columns)
        self.assertIn("idiomas_top", profile.columns)
        self.assertAlmostEqual(profile["participacion_pct"].sum(), 100.0)

    def test_full_run_writes_summary_findings_figures_and_model(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            result = run_analysis(
                make_books(),
                output_dir=root / "reportes",
                model_dir=root / "modelos",
                sample_size=120,
                validation_size=30,
            )

            self.assertTrue(result["summary_path"].is_file())
            self.assertTrue(result["findings_path"].is_file())
            self.assertTrue(result["model_path"].is_file())
            self.assertTrue(all(path.is_file() for path in result["figures"]))
            self.assertIn("Pregunta de negocio", result["summary_path"].read_text("utf-8"))
            self.assertIn("Recomendación", result["findings_path"].read_text("utf-8"))


if __name__ == "__main__":
    unittest.main()
