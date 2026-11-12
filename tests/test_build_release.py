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

    def test_pdf_validator_rejects_blank_pages(self):
        from pypdf import PdfWriter
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "blank-page.pdf"
            writer = PdfWriter()
            writer.add_blank_page(width=432, height=648)
            with path.open("wb") as stream:
                writer.write(stream)
            with self.assertRaisesRegex(AssertionError, "blank or page-number-only"):
                builder.validate_pdf_document(path, 6, 9)

    def test_arabic_chapter_19_matches_the_two_campuses_admissions_arc(self):
        text = builder.source_text(builder.AR)
        chapter19 = text.split("# الفصل التاسع عشر", 1)[1].split("# الفصل العشرون", 1)[0]
        self.assertIn("وصلت رسائل القبول الجامعي", chapter19)
        self.assertIn("أربعون دقيقة", chapter19)
        self.assertNotIn("بحلول نهاية العام الجامعي الثاني", chapter19)

    def test_pdf_cleanup_removes_bookmarks_links_and_embedded_files(self):
        from pypdf import PdfReader, PdfWriter
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "decorated.pdf"
            writer = PdfWriter()
            writer.add_blank_page(width=432, height=648)
            writer.add_outline_item("Bookmark", 0)
            writer.add_attachment("credential.txt", b"metadata")
            writer.add_annotation(0, {
                "/Type": "/Annot", "/Subtype": "/Text", "/Contents": "note",
                "/Rect": [0, 0, 10, 10]
            })
            with path.open("wb") as stream:
                writer.write(stream)
            builder.strip_pdf_print_artifacts(path)
            reader = PdfReader(str(path))
            self.assertEqual(len(reader.outline), 0)
            self.assertFalse(reader.attachments)
            self.assertTrue(all(not page.get("/Annots") for page in reader.pages))

    def test_arabic_kindle_source_has_one_front_matter_block(self):
        raw = builder.source_text(builder.AR)
        body = builder.prepare_arabic_body(raw)
        self.assertTrue(body.startswith("# الفصل الأول"))
        self.assertNotIn("المخطوطة العربية الكاملة", body)
        self.assertNotIn("نسخة موحّدة للمراجعة", body)
        self.assertNotIn("حقوق النشر © 2026", body)
