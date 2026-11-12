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
