# Production Master Plan
## A Gift from the One Who Left / هدية من الغائب

**Author (English):** Aly HUSSEIN FEKRY  
**English edition:** Kindle eBook + Paperback  
**Arabic edition:** Kindle eBook  
**Canonical story premise:** Michael dies in a car accident while driving to the wedding venue. The wedding never takes place. Michael and Emily do not marry; there is no honeymoon.

## Production source of truth

- Production branch: `production/prepress-organization`
- Story-correction source: `fix/wedding-day-death-canonical-manuscript`
- Story correction PR: [PR #4](https://github.com/zopair/Zubair-Publishing-Engine/pull/4) — currently open as Draft and not merged.
- English master: `manuscript/en/FULL-ENGLISH-MANUSCRIPT.md`
- Arabic master: `manuscript/ar/FULL-ARABIC-MANUSCRIPT.md`
- Chapter sources: `manuscript/en/` and `manuscript/ar/`
- Superseded English honeymoon/married-life drafts are retained only in `manuscript/archive/en/obsolete-wedding-arc/`; they are not canonical story content.

**Rule:** The consolidated master manuscripts are the assembly sources for formatting. Individual chapter files remain the editable source components. Archived drafts must never be included in a release export.

## Book structure

Both language masters currently contain:
- 36 numbered chapters
- 1 epilogue
- 2 narrative parts

See [MANUSCRIPT-MAP.md](./MANUSCRIPT-MAP.md) for the production map and bilingual chapter sequence.

## Release editions

| Edition | Format | Production route |
|---|---|---|
| English | Kindle eBook | Reflowable EPUB or DOCX; validate in Kindle Previewer and KDP Online Previewer |
| English | Paperback | Print-ready interior PDF + full-wrap cover PDF; dimensions fixed only after trim size, paper, and final page count |
| Arabic | Kindle eBook | RTL DOCX following KDP's Arabic Word workflow; validate in KDP Online Previewer |
| Arabic | Paperback | Not in the current release scope; KDP currently lists Arabic as eBook-only |

## Work sequence

1. **Freeze the canonical text**
   - Review and approve PR #4.
   - Confirm both consolidated masters match the intended 36-chapter + epilogue sequence.
   - Run one final focused continuity and bilingual integrity check; do not reopen optional stylistic edits.
2. **Prepare publication front matter**
   - Title page, copyright page, dedication (if approved), contents, and any author note.
   - Ensure the title and author display match KDP metadata exactly.
3. **Prepare the cover package**
   - Approve the creative direction in [COVER-DESIGN-BRIEF.md](./COVER-DESIGN-BRIEF.md).
   - Create the Kindle front cover first.
   - Create the English paperback full wrap only after final page count, trim size, and paper choice are known.
4. **Format the interiors**
   - English Kindle: reflowable EPUB/DOCX.
   - Arabic Kindle: true right-to-left DOCX, not right-aligned LTR text.
   - English paperback: print interior PDF with embedded fonts and correct margins/gutter.
5. **Complete metadata**
   - Resolve the Arabic-script author name.
   - Approve descriptions, keywords, categories, territories, marketplace, pricing, and KDP Select decision.
   - Confirm AI-generated content disclosure against the actual contribution history.
6. **Quality assurance and release**
   - Validate every edition in the appropriate KDP previewer.
   - Review the English paperback proof copy.
   - Obtain the author's explicit approval before any final KDP submission or publication.

## Current decisions and pending inputs

### Confirmed
- English author display: **Aly HUSSEIN FEKRY**
- English title: **A Gift from the One Who Left**
- Arabic title: **هدية من الغائب**
- Canonical wedding-day death premise as stated above.
- English paperback and Kindle; Arabic Kindle eBook.

### Pending before final files
- Arabic-script author name (must be supplied/confirmed by the author).
- Final trim size and paper type for the English paperback.
- Final page count after formatting; required for spine width.
- Cover direction approval and final cover artwork.
- Final descriptions, categories, keywords, price, primary marketplace, territories, and KDP Select choice.
- Final AI-content disclosure confirmation.

## Intellectual property and integrity

See [INTELLECTUAL-PROPERTY-AND-INTEGRITY.md](./INTELLECTUAL-PROPERTY-AND-INTEGRITY.md) for the inserted copyright notices, SHA-256 source fingerprints, evidence-preservation controls, Egypt deposit route, and KDP rights/AI-disclosure checklist.

## Official KDP references

- [Arabic publishing and Word formatting](https://kdp.amazon.com/en_US/help/topic/GUQT4C8J6RR6V8TY)
- [Supported languages](https://kdp.amazon.com/en_US/help/topic/G200673300)
- [Supported eBook manuscript formats](https://kdp.amazon.com/en_US/help/topic/G200634390)
- [Kindle Previewer](https://kdp.amazon.com/en_US/help/topic/G202131170)
- [AI-generated and AI-assisted content](https://kdp.amazon.com/en_US/help/topic/G200672390)
- [Metadata guidelines](https://kdp.amazon.com/en_US/help/topic/G201097560)
- [Paperback formatting](https://kdp.amazon.com/en_US/help/topic/G201834190)

## Release rule

No manuscript is to be silently rewritten during formatting. Formatting corrections may fix layout, typography, navigation, and technical compliance; any change to story wording must be logged and approved separately.