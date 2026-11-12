import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "publishing" / "build" / "build_release.py"
spec = importlib.util.spec_from_file_location("build_release", SCRIPT)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class ManuscriptValidationTests(unittest.TestCase):
    def test_current_english_master_passes_event_based_wedding_validation(self):
        text = builder.source_text(builder.EN)
        self.assertEqual(builder.assert_master(text, arabic=False), 36)

    def test_rejects_english_master_without_wedding_aftermath_in_chapter_31(self):
        text = builder.source_text(builder.EN)
        chapter31 = text.replace("There was no morning after the wedding.", "The day began normally.", 1)
        with self.assertRaisesRegex(AssertionError, "Chapter 31 must establish"):
            builder.assert_master(chapter31, arabic=False)

    def test_current_arabic_master_passes(self):
        text = builder.source_text(builder.AR)
        self.assertEqual(builder.assert_master(text, arabic=True), 36)


if __name__ == "__main__":
    unittest.main()


class KdpPrepressValidationTests(unittest.TestCase):
    def test_pdf_trim_validator_rejects_letter_page_when_6x9_is_required(self):
        with self.assertRaisesRegex(AssertionError, "PDF page size"):
            builder.validate_pdf_trim(612, 792, 6, 9)

    def test_pdf_trim_validator_accepts_exact_6x9_page(self):
        builder.validate_pdf_trim(432, 648, 6, 9)
