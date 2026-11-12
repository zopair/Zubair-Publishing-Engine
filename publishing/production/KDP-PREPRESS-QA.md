# KDP Prepress QA — A Gift from the One Who Left

Status: **release candidate; not approved for upload**

## Production configuration

- English paperback trim: 6 × 9 in
- Interior: black ink, cream paper, no bleed
- Interior typography: Noto Serif, 11 pt
- Interior margins: inside 0.78 in; outside 0.55 in; top/bottom 0.65 in
- Latest measured interior: 279 PDF pages
- KDP rounds an odd paperback page count up to an even count: 280 pages
- Cream-paper spine: 280 × 0.0025 in = 0.700 in
- Full-wrap cover including 0.125 in outer bleed: 12.950 × 9.250 in
- Cover export: one-page PDF, CMYK, 300 DPI, flattened, barcode reserve left blank (2 × 1.2 in)

## Automated print-PDF gates

The builder validates every page box against 6 × 9 in, rejects blank/page-number-only pages, checks embedded fonts, and strips bookmarks, annotations, embedded attachments, XMP metadata, and document-info metadata. It also rejects encrypted PDFs.

## Kindle deliverables

- English: reflowable EPUB with title, author, and English language metadata.
- Arabic: Word DOCX for Kindle conversion, with Arabic language metadata, paragraph RTL, run RTL, right alignment, and 0.2 in first-line body indents.
- The Arabic KDP export removes the archive-only review title and copyright block before adding one clean title/copyright front matter.

## Arabic language and continuity review

The merged Arabic and English manuscripts were compared against their chapter source files. The review identified and corrected:
- Chapter 13 Arabic chronology: restored the beginning of the summer program rather than its end.
- Chapter 19 Arabic translation: replaced duplicated Chapter 22 material with the university-admissions and two-campus story.
- Chapter 30 merged-master drift: synchronized the direct wedding-venue route so Michael dies while on his way to the ceremony.
- Additional Arabic grammar and fluency refinements in Chapters 1, 3, 8, 20, 24, 25, 26, 32, 33, 35, and 36.

This is a first editorial pass, not a claim that a professional human copyeditor has signed off on every line. Final linguistic approval remains a separate gate.

## KDP language limitation

KDP currently supports Arabic for Kindle eBooks, but not Arabic-language paperback printing. The Arabic release is therefore Kindle-only. The English release can include Kindle and paperback formats.

## Approval gates still required

1. Author approval of the English full-wrap paperback cover and Arabic Kindle cover.
2. Final visual review in Kindle Previewer and KDP Print Previewer.
3. Confirm the KDP print options match the assumptions above (6 × 9 in, black ink, cream paper, no bleed).
4. Complete KDP's AI-generated-content disclosure accurately before publication.

No file in this branch is authorized for upload or publication until the author approves the final previews.
