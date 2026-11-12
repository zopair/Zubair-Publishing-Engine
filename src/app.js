import { createProject, normalizeChapter, sortChapters, validateProject } from "./core/manuscript.js";
import { buildDocx, buildEpub, inspectProjectForExport } from "./core/exporters.js";

const STORAGE_KEY = "zubair-publishing-engine:v1";
const $ = (selector) => document.querySelector(selector);
const state = { project: null, activeChapterId: null };

function showToast(message) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.add("show");
  window.setTimeout(() => toast.classList.remove("show"), 2400);
}

function persist() {
  if (!state.project) return;
  state.project.updatedAt = new Date().toISOString();
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state.project));
    $("#export-project").disabled = false;
  } catch {
    showToast("تعذر الحفظ المحلي؛ مساحة المتصفح قد تكون ممتلئة.");
  }
}

function restore() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === "object" && Array.isArray(parsed.chapters)) {
      state.project = createProject(parsed);
      state.activeChapterId = state.project.chapters[0]?.id ?? null;
      fillProjectForm();
      renderChapters();
      updateQuality();
    }
  } catch {
    showToast("تعذر قراءة النسخة المحلية المحفوظة.");
  }
}

function fillProjectForm() {
  if (!state.project) return;
  $("#book-title").value = state.project.title;
  $("#book-author").value = state.project.author;
  $("#book-language").value = state.project.language;
  $("#book-description").value = state.project.description;
}

function renderChapters() {
  const chapters = sortChapters(state.project?.chapters ?? []);
  const select = $("#chapter-select");
  select.replaceChildren();
  for (const chapter of chapters) {
    const option = document.createElement("option");
    option.value = chapter.id;
    option.textContent = `${chapter.number}. ${chapter.title || "فصل بلا عنوان"}`;
    select.append(option);
  }
  const hasChapters = chapters.length > 0;
  select.disabled = !hasChapters;
  $("#add-chapter").disabled = !state.project;
  $("#chapter-empty").hidden = hasChapters;
  $("#chapter-form").hidden = !hasChapters;
  if (!hasChapters) {
    select.add(new Option("لا توجد فصول بعد", ""));
    return;
  }
  if (!chapters.some((chapter) => chapter.id === state.activeChapterId)) {
    state.activeChapterId = chapters[0].id;
  }
  select.value = state.activeChapterId;
  loadActiveChapter();
}

function loadActiveChapter() {
  const chapter = state.project?.chapters.find((item) => item.id === state.activeChapterId);
  if (!chapter) return;
  $("#chapter-title").value = chapter.title;
  $("#chapter-content").value = chapter.content;
  updateWordCount();
}

function updateWordCount() {
  const text = $("#chapter-content").value.trim();
  const count = text ? text.split(/\s+/u).length : 0;
  $("#word-count").textContent = `${count.toLocaleString("ar-EG")} كلمة`;
}

function updateQuality() {
  const result = state.project ? validateProject(state.project) : { valid: false, errors: [] };
  $("#quality-title").textContent = state.project ? (result.valid ? "المخطوطة سليمة مبدئياً" : "توجد نقاط تحتاج إلى مراجعة") : "لا يوجد مشروع محفوظ";
  $("#quality-detail").textContent = state.project
    ? `${state.project.chapters.length} فصل · ${result.errors.length} ملاحظة بنيوية`
    : "أنشئ كتاباً وأضف فصوله لبدء الفحص.";
  $("#run-validation").disabled = !state.project;
  const exportCheck = state.project ? inspectProjectForExport(state.project) : { valid: false };
  $("#export-docx").disabled = !exportCheck.valid;
  $("#export-epub").disabled = !exportCheck.valid || state.project?.language !== "en";
  $("#export-status").textContent = !state.project ? "أنشئ كتاباً أولاً." : !exportCheck.valid ? exportCheck.errors[0] : state.project.language === "ar" ? "المخطوطة العربية جاهزة لتصدير DOCX." : "المخطوطة الإنجليزية جاهزة لتصدير DOCX وEPUB.";
  const list = $("#validation-results");
  list.replaceChildren();
  for (const error of result.errors) {
    const item = document.createElement("li");
    item.textContent = error.message;
    list.append(item);
  }
}

$("#project-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const data = new FormData(event.currentTarget);
  const existing = state.project;
  state.project = createProject({
    ...(existing ?? {}),
    title: data.get("title"),
    author: data.get("author"),
    language: data.get("language"),
    description: data.get("description"),
    chapters: existing?.chapters ?? [],
    id: existing?.id,
    createdAt: existing?.createdAt,
  });
  persist();
  renderChapters();
  updateQuality();
  showToast("تم حفظ بيانات الكتاب على هذا الجهاز.");
});

$("#new-project").addEventListener("click", () => {
  if (state.project && !window.confirm("إنشاء كتاب جديد؟ صدّر نسخة احتياطية من المشروع الحالي أولاً إذا كنت تحتاجها.")) return;
  state.project = createProject({ title: "" });
  state.activeChapterId = null;
  $("#project-form").reset();
  $("#book-title").focus();
  renderChapters();
  updateQuality();
});

$("#add-chapter").addEventListener("click", () => {
  if (!state.project) return;
  const nextNumber = Math.max(0, ...state.project.chapters.map((chapter) => chapter.number)) + 1;
  const chapter = normalizeChapter({ number: nextNumber, title: `Chapter ${nextNumber}`, content: "" });
  chapter.id = globalThis.crypto?.randomUUID?.() ?? `chapter-${nextNumber}-${Date.now()}`;
  state.project.chapters.push(chapter);
  state.activeChapterId = chapter.id;
  persist();
  renderChapters();
  $("#chapter-title").focus();
  updateQuality();
});

$("#chapter-select").addEventListener("change", (event) => {
  state.activeChapterId = event.target.value;
  loadActiveChapter();
});

$("#chapter-content").addEventListener("input", updateWordCount);

$("#chapter-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const chapter = state.project?.chapters.find((item) => item.id === state.activeChapterId);
  if (!chapter) return;
  chapter.title = $("#chapter-title").value.trim();
  chapter.content = $("#chapter-content").value.trim();
  persist();
  renderChapters();
  updateQuality();
  showToast("تم حفظ الفصل.");
});

$("#run-validation").addEventListener("click", () => {
  updateQuality();
  showToast("اكتمل الفحص البنيوي الأولي.");
});

$("#export-docx").addEventListener("click", () => {
  if (!state.project) return;
  try {
    const data = buildDocx(state.project);
    downloadBlob(new Blob([data], { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" }), `${safeFilename(state.project.title)}.docx`);
    showToast("تم إنشاء ملف DOCX.");
  } catch (error) { showToast(error.message); }
});

$("#export-epub").addEventListener("click", () => {
  if (!state.project) return;
  try {
    const data = buildEpub(state.project);
    downloadBlob(new Blob([data], { type: "application/epub+zip" }), `${safeFilename(state.project.title)}.epub`);
    showToast("تم إنشاء ملف EPUB.");
  } catch (error) { showToast(error.message); }
});

$("#export-project").addEventListener("click", () => {
  if (!state.project) return;
  const blob = new Blob([JSON.stringify(state.project, null, 2)], { type: "application/json;charset=utf-8" });
  downloadBlob(blob, `${safeFilename(state.project.title || "book")}-backup.json`);
});

function safeFilename(value) {
  return String(value).toLowerCase().replace(/[^a-z0-9\u0600-\u06ff]+/g, "-").replace(/^-|-$/g, "") || "book";
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

restore();
if ("serviceWorker" in navigator && location.protocol.startsWith("http")) {
  window.addEventListener("load", () => navigator.serviceWorker.register("./service-worker.js").catch(() => {}));
}