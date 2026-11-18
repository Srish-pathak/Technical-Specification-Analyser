"""Unit tests for PDF Technical Specification Analyzer."""
import unittest
import tempfile
from pathlib import Path

from app.models.database import Database
from app.services import pdf_service
from app.services.file_manager import InputValidationError


class TestPdfService(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.temp_dir.name) / "test.db")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_sample_pdf_generation_and_extraction(self):
        sample_bytes = pdf_service.generate_sample_pdf_bytes()
        self.assertGreater(len(sample_bytes), 500)

        pages, meta = pdf_service.extract_pdf_pages(sample_bytes, "Sample_Spec.pdf")
        self.assertEqual(meta["page_count"], 3)
        self.assertTrue(meta["has_text"])
        self.assertGreater(meta["total_words"], 100)
        self.assertEqual(len(pages), 3)
        self.assertEqual(pages[0]["page_number"], 1)
        self.assertIn("Cloud Analytics Platform", pages[0]["text"])

    def test_empty_pdf_raises_validation_error(self):
        with self.assertRaises(InputValidationError) as ctx:
            pdf_service.extract_pdf_pages(b"", "empty.pdf")
        self.assertEqual(ctx.exception.code, "pdf_empty")

    def test_corrupted_pdf_raises_validation_error(self):
        with self.assertRaises(InputValidationError) as ctx:
            pdf_service.extract_pdf_pages(b"%PDF-1.4\ncorrupted bytes not a real pdf", "corrupt.pdf")
        self.assertEqual(ctx.exception.code, "pdf_invalid")

    def test_complete_pdf_analysis_workflow(self):
        sample_bytes = pdf_service.generate_sample_pdf_bytes()
        result = pdf_service.process_and_analyze_pdf(sample_bytes, "Enterprise_Analytics.pdf")

        # Top-level keys
        self.assertIn("analysis_id", result)
        self.assertTrue(result["analysis_id"].startswith("A-pdf-"))
        self.assertEqual(result["input_type"], "pdf")
        self.assertEqual(result["status"], "completed")

        # Quality Score
        qs = result["quality_score"]
        self.assertIn("overall_score", qs)
        self.assertGreaterEqual(qs["overall_score"], 0)
        self.assertLessEqual(qs["overall_score"], 100)
        self.assertIn(qs["quality_level"], ["Excellent", "Good", "Needs Improvement", "Poor"])
        self.assertIn("category_scores", qs)
        self.assertIn("completeness", qs["category_scores"])
        self.assertIn("security", qs["category_scores"])
        self.assertIn("performance", qs["category_scores"])
        self.assertIn("architecture", qs["category_scores"])
        self.assertTrue(len(qs["strengths"]) > 0)
        self.assertTrue(len(qs["weaknesses"]) > 0)

        # Extracted Specifications
        specs = result["extracted_specifications"]
        self.assertTrue(len(specs["functional_requirements"]) > 0)
        self.assertTrue(len(specs["non_functional_requirements"]) > 0)
        self.assertTrue(len(specs["architecture"]) > 0)
        self.assertTrue(len(specs["tech_stack"]) > 0)
        self.assertTrue(len(specs["security"]) > 0)

        # Traceability Matrix
        tm = result["traceability_matrix"]
        self.assertGreaterEqual(len(tm), 3)
        for req in tm:
            self.assertIn("req_id", req)
            self.assertIn("category", req)
            self.assertIn("description", req)
            self.assertIn("source_page", req)
            self.assertIn("status", req)

        # Findings & Severity Classifications
        findings = result["findings"]
        severities = {f["severity"] for f in findings}
        self.assertTrue(any(s in ("Critical", "Warning", "Informational", "Passed") for s in severities))
        for f in findings:
            self.assertIn("title", f)
            self.assertIn("why_it_matters", f)
            self.assertIn("recommended_action", f)

        # Missing Gaps
        gaps = result["missing_gaps"]
        self.assertIsInstance(gaps, list)
        for g in gaps:
            self.assertIn("issue", g)
            self.assertIn("severity", g)
            self.assertIn("suggested_improvement", g)

        # AI Insights
        ai = result["ai_insights"]
        self.assertIn("executive_summary", ai)
        self.assertIn("key_observations", ai)
        self.assertIn("clarity_assessment", ai)
        self.assertIn("recommendations", ai)

        # Database Persistence & History
        self.db.save(result)
        fetched = self.db.get(result["analysis_id"])
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["analysis_id"], result["analysis_id"])

        hist = self.db.list()
        self.assertTrue(any(item["id"] == result["analysis_id"] for item in hist))

    def test_sample_pdf_download_response(self):
        from app.api.routes.analysis import download_sample_pdf
        resp = download_sample_pdf()
        self.assertEqual(resp.media_type, "application/pdf")
        self.assertIn("TechSpecAnalyser_Sample_Specification.pdf", resp.headers.get("content-disposition", ""))
        self.assertGreater(len(resp.body), 1000)
        self.assertTrue(resp.body.startswith(b"%PDF"))

    def test_unsupported_non_technical_document_rejection(self):
        """Verify that a non-software/non-engineering PDF is identified as unsupported without fake data."""
        unsupported_bytes = pdf_service.generate_sample_unsupported_pdf_bytes()
        result = pdf_service.process_and_analyze_pdf(unsupported_bytes, "Baking_Guide.pdf")

        self.assertEqual(result["status"], "unsupported")
        self.assertFalse(result["is_software_engineering_doc"])
        self.assertEqual(result["document_type"], "unsupported_non_technical")
        self.assertIsNotNone(result["rejection_reason"])
        self.assertIn("not appear to be a software", result["rejection_reason"].lower())
        # Ensure no hallucinated / fabricated requirements
        self.assertEqual(len(result["extracted_specifications"]), 0)
        self.assertEqual(len(result["traceability_matrix"]), 0)
        self.assertEqual(len(result["findings"]), 0)

    def test_generate_analysis_report_pdf(self):
        """Verify that generate_analysis_report_pdf outputs a valid multi-page PDF."""
        sample_bytes = pdf_service.generate_sample_pdf_bytes()
        result = pdf_service.process_and_analyze_pdf(sample_bytes, "Analytics_SRS.pdf")
        report_pdf_bytes = pdf_service.generate_analysis_report_pdf(result)

        self.assertGreater(len(report_pdf_bytes), 2000)
        self.assertTrue(report_pdf_bytes.startswith(b"%PDF"))

    def test_pdf_report_generation_for_database_record(self):
        """Verify that generate_analysis_report_pdf works on database-persisted records."""
        sample_bytes = pdf_service.generate_sample_pdf_bytes()
        result = pdf_service.process_and_analyze_pdf(sample_bytes, "Audit_Target.pdf")
        self.db.save(result)

        saved_rec = self.db.get(result["analysis_id"])
        self.assertIsNotNone(saved_rec)
        report_bytes = pdf_service.generate_analysis_report_pdf(saved_rec)
        self.assertGreater(len(report_bytes), 2000)
        self.assertTrue(report_bytes.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
