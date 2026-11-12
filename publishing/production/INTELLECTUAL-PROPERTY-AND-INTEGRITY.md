# Intellectual Property and Digital Integrity Record
## A Gift from the One Who Left / هدية من الغائب

**Record date:** 2026-11-12  
**Author display name supplied for English edition:** Aly HUSSEIN FEKRY  
**Canonical source branch:** `production/ip-protection-and-digital-fingerprints`

## 1. Copyright notice inserted into both consolidated manuscripts

- English master: `manuscript/en/FULL-ENGLISH-MANUSCRIPT.md`
- Arabic master: `manuscript/ar/FULL-ARABIC-MANUSCRIPT.md`

Both masters now contain a copyright notice near the front and a SHA-256 integrity fingerprint at the end.

## 2. SHA-256 source fingerprints

Algorithm: SHA-256 over UTF-8 bytes. The digest covers the exact consolidated manuscript content from the beginning through the copyright notice and all narrative text, excluding the final fingerprint section itself. This avoids the circular problem of trying to hash a file containing its own hash.

| Edition | SHA-256 digest |
|---|---|
| English source manuscript | `1c986b67e482d22cf20588f58ab8ef1a5e9f31f23a9194ed69216fdcccbbd3e5` |
| Arabic source manuscript | `3188b7bb4639b6f52e6a20efe332b6d4eab5b2bfff60df1c8d07d8cf7306720e` |

These are source-text fingerprints, not the hashes of the final EPUB, DOCX, PDF, or cover files. Generate and append a separate release manifest with hashes for every final distribution artifact after formatting/export. Never reuse these source digests as final-file hashes.

## 3. What the fingerprint does and does not prove

- SHA-256 is a cryptographic one-way hash used to detect changes in the hashed bytes.
- Anyone holding the exact text can independently recalculate and compare the digest.
- A matching digest supports integrity checking and version identification.
- A hash alone does not prove who authored a work, when it was created, or who owns copyright.
- A hash is not encryption, a digital signature, a timestamp authority, a copyright registration, or a substitute for evidence of authorship and chain of title.

## 4. Evidence preservation procedure

For a defensible evidence package, preserve together:
1. The exact source manuscripts and all final exported release files.
2. This manifest and the corresponding Git commit IDs.
3. Dated drafts, revision history, editorial notes, correspondence, and records showing the author's creative decisions and approvals.
4. Cover artwork source files, font/image licences, and contributor agreements.
5. Any translation, editing, illustration, or publishing agreements specifying rights granted and retained.
6. Copies of official deposit/registration receipts, ISBN records, and publication dates when obtained.

Recommended operational controls:
- Enable GitHub two-factor authentication and use least-privilege repository access.
- Keep at least two independent backups of the release package.
- After final approval, create a versioned release tag and preserve a signed tag if the author controls a signing key.
- Do not overwrite released artifacts; issue a new version and new hashes for every substantive update.
- Keep private working drafts and proof documents access-controlled. Public repository history is useful evidence but should not be the only evidence archive.

## 5. Egypt: official deposit and rights route

Copyright protection is generally automatic for eligible original works under the Berne framework; voluntary registration/deposit can provide useful evidence but does not replace proof of authorship or ownership.

For publication in Egypt, verify the current process directly with the National Library and Archives of Egypt (Dar al-Kotob) before filing. Its official book-deposit service publishes the required documents, online submission steps, and post-issuance deposit obligations. Requirements differ depending on whether the applicant is an author-publisher, publisher, or printer, and whether the edition is print or electronic.

Official starting points:
- Dar al-Kotob book deposit service: https://www.darelkotob.gov.eg/ar-eg/Pages/PeriodicalPrintingService.aspx
- Required documents for deposit: https://www.darelkotob.gov.eg/ar-eg/Documents/%D8%A7%D9%84%D8%A7%D9%8A%D8%AF%D8%A7%D8%B9/%D8%A7%D9%84%D8%A7%D9%88%D8%B1%D8%A7%D9%82%20%D8%A7%D9%84%D9%85%D8%B7%D9%84%D9%88%D8%A8%D8%A9%20%D9%84%D9%84%D9%86%D8%A7%D8%B4%D8%B1%D9%8A%D9%86.pdf
- Official submission steps: https://www.darelkotob.gov.eg/ar-eg/Documents/%D8%A7%D9%84%D8%A7%D9%8A%D8%AF%D8%A7%D8%B9/%D8%B7%D8%B1%D9%82%20%D8%A7%D9%84%D8%AA%D9%82%D8%AF%D9%8A%D9%85.pdf
- Egyptian Authority for Intellectual Property information: https://sis.gov.eg/en/egypt/culture/cultural-institutions/egyptian-authority-for-intellectual-property/

**Status:** No government registration, deposit number, ISBN, notarized certificate, or official filing has been obtained by this repository change. Those require a formal application and the relevant authority's acceptance.

## 6. KDP rights and AI disclosure

Before KDP submission:
- Confirm the author/rightsholder identity and that all necessary publishing rights are held.
- Preserve permission/licence evidence for any third-party text, images, fonts, or other assets.
- Complete KDP's AI-generated content disclosure accurately. KDP states that AI-generated text, images, and translations must be disclosed; AI-assisted editing alone is treated differently.
- Do not claim exclusive copyright over material that applicable law does not recognize as human-authored protectable expression. Preserve the human creative contribution, selection, revision, arrangement, and authorship evidence.

Official KDP references:
- Intellectual property rights: https://kdp.amazon.com/en_US/help/topic/G200672400
- AI-generated content disclosure: https://kdp.amazon.com/en_US/help/topic/G200672390

## 7. Outstanding actions before publication

- [ ] Confirm the Arabic-script author name before final Arabic cover/title metadata.
- [ ] Review and approve both inserted copyright notices.
- [ ] Confirm the rights-holder identity and chain of title; sign any required declarations.
- [ ] Verify the exact current Egyptian deposit requirements and submit the relevant application.
- [ ] Obtain and archive any official deposit/registration documents.
- [ ] After final formatting, calculate SHA-256 for each final EPUB/DOCX/PDF/cover file and create a release-specific manifest.
- [ ] Complete KDP AI-generated content disclosure at upload.
- [ ] Obtain explicit author approval before publishing or licensing the work.

## 8. Change control

Any substantive manuscript edit invalidates the affected source fingerprint. Recalculate it and update the manuscript endnote and this manifest together. Formatting-only exports receive their own file hashes and release identifiers.
