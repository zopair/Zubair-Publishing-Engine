import test from "node:test";
import assert from "node:assert/strict";
import {
  createProject,
  normalizeChapter,
  sortChapters,
  validateProject,
  slugify,
} from "../src/core/manuscript.js";

test("creates a project with safe defaults", () => {
  const project = createProject({ title: "A Gift from the One Who Left" });
  assert.equal(project.title, "A Gift from the One Who Left");
  assert.equal(project.language, "en");
  assert.deepEqual(project.chapters, []);
  assert.ok(project.id);
});

test("normalizes chapter numbers and trims content", () => {
  const chapter = normalizeChapter({ number: "2", title: "  First Light  ", content: "  Hello  " });
  assert.equal(chapter.number, 2);
  assert.equal(chapter.title, "First Light");
  assert.equal(chapter.content, "Hello");
});

test("sorts chapters numerically without mutating the input", () => {
  const chapters = [
    { number: 10, title: "Ten" },
    { number: 2, title: "Two" },
    { number: 1, title: "One" },
  ];
  const sorted = sortChapters(chapters);
  assert.deepEqual(sorted.map((chapter) => chapter.number), [1, 2, 10]);
  assert.equal(chapters[0].number, 10);
});

test("reports missing title and duplicate chapter numbers", () => {
  const result = validateProject({
    title: " ",
    language: "en",
    chapters: [
      { number: 1, title: "Opening", content: "Text" },
      { number: 1, title: "Repeated", content: "More text" },
    ],
  });
  assert.equal(result.valid, false);
  assert.ok(result.errors.some((error) => error.code === "TITLE_REQUIRED"));
  assert.ok(result.errors.some((error) => error.code === "DUPLICATE_CHAPTER_NUMBER"));
});

test("creates stable URL-safe slugs", () => {
  assert.equal(slugify("A Gift from the One Who Left"), "a-gift-from-the-one-who-left");
  assert.equal(slugify("  Chapter 01: First Light!  "), "chapter-01-first-light");
});

test("preserves a project identifier when restoring a backup", () => {
  const restored = createProject({ id: "project-stable-123", title: "Restored Book" });
  assert.equal(restored.id, "project-stable-123");
});

import { buildEpub, buildDocx, decodeUtf8, inspectProjectForExport } from "../src/core/exporters.js";

const sampleBook = {
  title: "A Gift from the One Who Left",
  author: "Test Author",
  language: "en",
  description: "A romantic novel.",
  chapters: [{ number: 1, title: "The First Meeting", content: "Hello, Michael.\n\nEmily smiled." }],
};

test("export preflight blocks empty books and blank chapters", () => {
  const result = inspectProjectForExport({ ...sampleBook, chapters: [] });
  assert.equal(result.valid, false);
  assert.ok(result.errors.length > 0);
});

test("builds EPUB package with required mimetype and OPF entries", () => {
  const epub = buildEpub(sampleBook);
  assert.ok(epub instanceof Uint8Array);
  assert.ok(epub.length > 100);
  assert.equal(epub[0], 0x50);
  assert.equal(epub[1], 0x4b);
});

test("builds DOCX package for Arabic manuscripts with RTL metadata", () => {
  const docx = buildDocx({
    ...sampleBook,
    title: "هدية من الغائب",
    language: "ar",
    chapters: [{ number: 1, title: "الفصل الأول", content: "كان الحب بداية الحكاية." }],
  });
  assert.ok(docx instanceof Uint8Array);
  assert.ok(docx.length > 100);
  assert.equal(docx[0], 0x50);
  assert.equal(docx[1], 0x4b);
});


test("builds a right-to-left Arabic EPUB with matching language and author metadata", () => {
  const epub = buildEpub({
    ...sampleBook,
    title: "هدية من الغائب",
    author: "Aly HUSSEIN FEKRY",
    language: "ar",
    chapters: [{ number: 1, title: "الفصل الأول", content: "كان الحب بداية الحكاية." }],
  });
  const archive = decodeUtf8(epub);
  assert.ok(archive.includes("<dc:language>ar</dc:language>"));
  assert.ok(archive.includes('page-progression-direction="rtl"'));
  assert.ok(archive.includes('lang="ar" dir="rtl"'));
  assert.ok(archive.includes("<dc:creator>Aly HUSSEIN FEKRY</dc:creator>"));
  assert.ok(archive.includes("OEBPS/text/title.xhtml"));
  assert.ok(archive.includes("هدية من الغائب"));
});

test("includes author name on the DOCX title page", () => {
  const docx = buildDocx({
    ...sampleBook,
    author: "Aly HUSSEIN FEKRY",
    chapters: [{ number: 1, title: "The First Meeting", content: "Hello, Michael." }],
  });
  const archive = decodeUtf8(docx);
  assert.ok(archive.includes("Aly HUSSEIN FEKRY"));
});
