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

    def test_arabic_docx_has_rtl_direction_and_first_line_indents(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "arabic.docx"
            builder.make_arabic_docx(builder.AR, target)
            builder.validate_arabic_docx(target)

    def test_arabic_chapter_13_matches_the_english_summer_program_start(self):
        text = builder.source_text(builder.AR)
        chapter13 = text.split("# الفصل الثالث عشر", 1)[1].split("# الفصل الرابع عشر", 1)[0]
        self.assertIn("بدأ الأسبوع الأول من البرنامج الصيفي", chapter13)
        self.assertNotIn("بحلول نهاية الصيف", chapter13)

    def test_pdf_validator_rejects_pages_containing_only_a_page_number(self):
        from reportlab.pdfgen import canvas
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "blank-page.pdf"
            c = canvas.Canvas(str(path), pagesize=(432, 648))
            c.drawString(200, 30, "12")
            c.showPage(); c.save()
            with self.assertRaisesRegex(AssertionError, "blank or page-number-only"):
                builder.validate_pdf_document(path, 6, 9)

    def test_arabic_chapter_19_matches_the_two_campuses_admissions_arc(self):
        text = builder.source_text(builder.AR)
        chapter19 = text.split("# الفصل التاسع عشر", 1)[1].split("# الفصل العشرون", 1)[0]
        self.assertIn("وصلت رسائل القبول الجامعي", chapter19)
        self.assertIn("أربعون دقيقة", chapter19)
        self.assertNotIn("بحلول نهاية العام الجامعي الثاني", chapter19)
