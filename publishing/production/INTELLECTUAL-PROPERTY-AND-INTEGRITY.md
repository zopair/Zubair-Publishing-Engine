# Intellectual Property and Digital Integrity Record
## A Gift from the One Who Left / هدية من الغائب

**Record date:** 2026-11-12  
**Author display name — English:** Aly HUSSEIN FEKRY  
**Author display name — Arabic:** على حسين فكرى  
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
| Arabic source manuscript | `d640b8c4cea88b05b1e7a7f490bc0ac09a8fca5ea4bbe640c955460c40b3f5e7` |

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

## 5. Chosen evidence approach: GitHub repository only

**Author's decision:** No deposit or registration application will be pursued in Egypt for this release. The selected evidence archive is the project's GitHub repository.

Repository evidence to preserve:
- The exact bilingual source manuscripts and their SHA-256 fingerprints.
- Git commit history and pull-request review records for manuscript and production changes.
- The final approved release tag/commit and a release-specific SHA-256 manifest for each exported EPUB, DOCX, PDF, and cover file.
- Author approvals, dated drafts, editorial decisions, source artwork, and third-party licences/permissions where applicable.

**Important limitation:** GitHub history and SHA-256 fingerprints provide version and integrity evidence. They are not a government registration, official timestamp certificate, notarized record, or conclusive legal determination of authorship/ownership. Keep independent backups of the exact release package. No Egyptian deposit, registration number, ISBN, or government filing is claimed.

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

- [x] Arabic-script author display confirmed: **على حسين فكرى**.
- [ ] Review and approve both inserted copyright notices and the Arabic author attribution.
- [ ] Confirm the rights-holder identity and chain of title; sign any required declarations.
- [ ] After final formatting, calculate SHA-256 for each final EPUB/DOCX/PDF/cover file and create a release-specific manifest.
- [ ] Complete KDP AI-generated content disclosure at upload.
- [ ] Obtain explicit author approval before publishing or licensing the work.

## 8. Change control

Any substantive manuscript edit invalidates the affected source fingerprint. Recalculate it and update the manuscript endnote and this manifest together. Formatting-only exports receive their own file hashes and release identifiers.
