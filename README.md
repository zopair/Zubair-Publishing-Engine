# Zubair Publishing Engine

A mobile-first, local-first publishing workspace designed to help prepare manuscripts for Kindle Direct Publishing (KDP), starting from an Android phone.

## Current milestone: foundation

- Responsive Arabic-first workspace.
- Local browser storage; no account or paid backend required.
- Book metadata and chapter editor.
- Basic manuscript structure validation.
- JSON backup export.
- Installable PWA shell with offline asset caching.
- Zero-dependency Node.js test suite.

## Run locally

Requires Node.js 20+ for tests. The application itself is static HTML/CSS/JavaScript and can be served by any static web server.

```bash
npm test
python -m http.server 8080
```

Open `http://localhost:8080`.

## Architecture

- `src/core/`: pure manuscript domain logic.
- `src/app.js`: browser application and local persistence.
- `tests/`: Node built-in test runner.
- `service-worker.js`: offline application shell.
- `manifest.webmanifest`: installable PWA metadata.

## Product principles

1. Mobile-first; optimize for Android browsers and modest devices.
2. Local-first; user manuscripts remain in the browser unless explicitly exported.
3. Zero recurring cost; avoid mandatory paid services and external runtime dependencies.
4. Separate English and Arabic publishing paths, including correct RTL handling.
5. Validate every generated artifact before it is considered publish-ready.
6. KDP upload and final publication remain human-approved actions.

## Roadmap

- [x] Repository and mobile-first application foundation.
- [x] Manuscript project model and validation tests.
- [x] Chapter editor and local JSON backup.
- [ ] Import and export DOCX.
- [ ] Generate and validate reflowable EPUB for English.
- [ ] Arabic DOCX/EPUB preparation and RTL verification.
- [ ] Cover specification and metadata package.
- [ ] KDP preflight checklist and preview workflow.
- [ ] Paperback interior PDF and print cover calculations.

## Important

The current application is an early foundation, not yet a complete EPUB/DOCX production tool. Do not upload its current exports as finished KDP manuscripts. Always inspect final files with KDP Previewer or KDP's online preview before publication.
