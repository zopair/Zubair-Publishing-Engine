const SUPPORTED_LANGUAGES = new Set(["en", "ar"]);

export function createProject(input = {}) {
  const title = String(input.title ?? "").trim();
  return {
    id: String(input.id ?? globalThis.crypto?.randomUUID?.() ?? `project-${Date.now().toString(36)}`),
    title,
    language: SUPPORTED_LANGUAGES.has(input.language) ? input.language : "en",
    author: String(input.author ?? "").trim(),
    description: String(input.description ?? "").trim(),
    chapters: Array.isArray(input.chapters) ? input.chapters.map(normalizeChapter) : [],
    createdAt: input.createdAt ?? new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    schemaVersion: 1,
  };
}

export function normalizeChapter(input = {}) {
  const number = Number.parseInt(input.number, 10);
  return {
    id: String(input.id ?? `chapter-${Number.isFinite(number) ? number : "new"}`),
    number: Number.isFinite(number) && number > 0 ? number : 0,
    title: String(input.title ?? "").trim(),
    content: String(input.content ?? "").trim(),
  };
}

export function sortChapters(chapters = []) {
  return [...chapters].sort((a, b) => Number(a.number) - Number(b.number));
}

export function validateProject(project = {}) {
  const errors = [];
  const title = String(project.title ?? "").trim();
  const chapters = Array.isArray(project.chapters) ? project.chapters : [];

  if (!title) {
    errors.push({ code: "TITLE_REQUIRED", message: "Book title is required." });
  }

  if (!SUPPORTED_LANGUAGES.has(project.language)) {
    errors.push({ code: "LANGUAGE_UNSUPPORTED", message: "Choose English or Arabic." });
  }

  const seenNumbers = new Set();
  for (const chapter of chapters) {
    const number = Number(chapter.number);
    if (!Number.isInteger(number) || number < 1) {
      errors.push({
        code: "CHAPTER_NUMBER_INVALID",
        message: `Chapter "${String(chapter.title ?? "Untitled")}" needs a positive whole number.`,
      });
      continue;
    }
    if (seenNumbers.has(number)) {
      errors.push({
        code: "DUPLICATE_CHAPTER_NUMBER",
        message: `Chapter number ${number} is used more than once.`,
      });
    }
    seenNumbers.add(number);
    if (!String(chapter.title ?? "").trim()) {
      errors.push({ code: "CHAPTER_TITLE_REQUIRED", message: `Chapter ${number} needs a title.` });
    }
  }

  return { valid: errors.length === 0, errors };
}

export function slugify(value = "") {
  return String(value)
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}