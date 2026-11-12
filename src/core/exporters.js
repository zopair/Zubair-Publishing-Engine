const encoder = new TextEncoder();
const decoder = new TextDecoder();

function xml(value = "") {
  return String(value).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&apos;");
}

function bytes(value) {
  return value instanceof Uint8Array ? value : encoder.encode(String(value));
}

function crc32(data) {
  let crc = 0xffffffff;
  for (const byte of data) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit += 1) crc = (crc >>> 1) ^ (0xedb88320 & -(crc & 1));
  }
  return (crc ^ 0xffffffff) >>> 0;
}

function u16(view, offset, value) { view.setUint16(offset, value, true); }
function u32(view, offset, value) { view.setUint32(offset, value >>> 0, true); }

/** Creates a standards-compliant ZIP archive using STORE (no compression). */
export function createZip(entries) {
  const localParts = [];
  const centralParts = [];
  let offset = 0;

  for (const entry of entries) {
    const name = bytes(entry.name);
    const data = bytes(entry.data);
    const crc = crc32(data);
    const local = new Uint8Array(30 + name.length);
    const lv = new DataView(local.buffer);
    u32(lv, 0, 0x04034b50); u16(lv, 4, 20); u16(lv, 6, 0x0800);
    u16(lv, 8, 0); u16(lv, 10, 0); u16(lv, 12, 0);
    u32(lv, 14, crc); u32(lv, 18, data.length); u32(lv, 22, data.length);
    u16(lv, 26, name.length); u16(lv, 28, 0); local.set(name, 30);
    localParts.push(local, data);

    const central = new Uint8Array(46 + name.length);
    const cv = new DataView(central.buffer);
    u32(cv, 0, 0x02014b50); u16(cv, 4, 20); u16(cv, 6, 20);
    u16(cv, 8, 0x0800); u16(cv, 10, 0); u16(cv, 12, 0); u16(cv, 14, 0);
    u32(cv, 16, crc); u32(cv, 20, data.length); u32(cv, 24, data.length);
    u16(cv, 28, name.length); u16(cv, 30, 0); u16(cv, 32, 0);
    u16(cv, 34, 0); u16(cv, 36, 0); u32(cv, 38, 0); u32(cv, 42, offset);
    central.set(name, 46);
    centralParts.push(central);
    offset += local.length + data.length;
  }

  const centralSize = centralParts.reduce((sum, part) => sum + part.length, 0);
  const end = new Uint8Array(22);
  const ev = new DataView(end.buffer);
  u32(ev, 0, 0x06054b50); u16(ev, 4, 0); u16(ev, 6, 0);
  u16(ev, 8, entries.length); u16(ev, 10, entries.length);
  u32(ev, 12, centralSize); u32(ev, 16, offset); u16(ev, 20, 0);

  const total = offset + centralSize + end.length;
  const output = new Uint8Array(total);
  let cursor = 0;
  for (const part of [...localParts, ...centralParts, end]) {
    output.set(part, cursor);
    cursor += part.length;
  }
  return output;
}

function normalized(project) {
  const chapters = [...(project.chapters ?? [])].sort((a, b) => Number(a.number) - Number(b.number));
  return { ...project, chapters };
}

export function inspectProjectForExport(project = {}) {
  const errors = [];
  if (!String(project.title ?? "").trim()) errors.push("عنوان الكتاب مطلوب.");
  if (!String(project.author ?? "").trim()) errors.push("اسم المؤلف مطلوب لبيانات النشر.");
  if (!["en", "ar"].includes(project.language)) errors.push("لغة الكتاب يجب أن تكون الإنجليزية أو العربية.");
  const chapters = Array.isArray(project.chapters) ? project.chapters : [];
  if (!chapters.length) errors.push("أضف فصلاً واحداً على الأقل.");
  const seen = new Set();
  for (const chapter of chapters) {
    const number = Number(chapter.number);
    if (!Number.isInteger(number) || number < 1) errors.push("يوجد فصل برقم غير صالح.");
    if (seen.has(number)) errors.push(`رقم الفصل ${number} مكرر.`);
    seen.add(number);
    if (!String(chapter.title ?? "").trim()) errors.push(`عنوان الفصل ${number} مطلوب.`);
    if (!String(chapter.content ?? "").trim()) errors.push(`محتوى الفصل ${number} فارغ.`);
  }
  return { valid: errors.length === 0, errors };
}

function requireValid(project) {
  const result = inspectProjectForExport(project);
  if (!result.valid) throw new Error(result.errors.join(" "));
  return normalized(project);
}

function paragraphs(text, language) {
  const rtl = language === "ar";
  return String(text).split(/\r?\n/).map((line) => {
    const safe = xml(line);
    if (!safe) return "<p/>";
    return rtl
      ? `<p class="body" dir="rtl"><span>${safe}</span></p>`
      : `<p class="body"><span>${safe}</span></p>`;
  }).join("\n");
}

export function buildEpub(input) {
  const project = requireValid(input);
  const language = project.language;
  const rtl = language === "ar";
  const direction = rtl ? "rtl" : "ltr";
  const contentsLabel = rtl ? "المحتويات" : "Contents";
  const identifier = xml(project.id ?? project.title);
  const title = xml(project.title);
  const author = xml(project.author.trim());
  const description = xml(project.description || "");
  const manifest = `<item id="title" href="text/title.xhtml" media-type="application/xhtml+xml"/>` + project.chapters.map((chapter, index) =>
    `<item id="chapter-${index + 1}" href="text/chapter-${index + 1}.xhtml" media-type="application/xhtml+xml"/>`
  ).join("");
  const spine = `<itemref idref="title"/>` + project.chapters.map((_, index) => `<itemref idref="chapter-${index + 1}"/>`).join("");
  const entries = [
    { name: "mimetype", data: "application/epub+zip" },
    { name: "META-INF/container.xml", data: '<?xml version="1.0" encoding="UTF-8"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>' },
    { name: "OEBPS/styles/book.css", data: "body{font-family:serif;line-height:1.7;margin:5%;}h1{text-align:center;margin:2em 0;}p{orphans:2;widows:2;text-indent:1.2em;} .body:first-child{text-indent:0;}body[dir=\"rtl\"]{direction:rtl;text-align:right;}body[dir=\"ltr\"]{direction:ltr;text-align:left;}.author{text-align:center;text-indent:0;margin-top:2em;}" },
    { name: "OEBPS/content.opf", data: `<?xml version="1.0" encoding="UTF-8"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="book-id" xml:lang="${language}"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="book-id">${identifier}</dc:identifier><dc:title>${title}</dc:title><dc:language>${language}</dc:language><dc:creator>${author}</dc:creator><dc:description>${description}</dc:description><meta property="dcterms:modified">2026-11-12T00:00:00Z</meta></metadata><manifest><item id="nav" href="nav.xhtml" properties="nav" media-type="application/xhtml+xml"/><item id="css" href="styles/book.css" media-type="text/css"/>${manifest}</manifest><spine${rtl ? ' page-progression-direction="rtl"' : ""}>${spine}</spine></package>` },
    { name: "OEBPS/nav.xhtml", data: `<?xml version="1.0" encoding="UTF-8"?><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="${language}" xml:lang="${language}" dir="${direction}"><head><title>${contentsLabel}</title></head><body dir="${direction}"><nav epub:type="toc"><h1>${contentsLabel}</h1><ol>${project.chapters.map((chapter, index) => `<li><a href="text/chapter-${index + 1}.xhtml">${xml(chapter.title)}</a></li>`).join("")}</ol></nav></body></html>` },
    { name: "OEBPS/text/title.xhtml", data: `<?xml version="1.0" encoding="UTF-8"?><html xmlns="http://www.w3.org/1999/xhtml" lang="${language}" xml:lang="${language}" dir="${direction}"><head><title>${title}</title><link rel="stylesheet" type="text/css" href="../styles/book.css"/></head><body dir="${direction}"><h1>${title}</h1><p class="author">${author}</p></body></html>` },
    ...project.chapters.map((chapter, index) => ({
      name: `OEBPS/text/chapter-${index + 1}.xhtml`,
      data: `<?xml version="1.0" encoding="UTF-8"?><html xmlns="http://www.w3.org/1999/xhtml" lang="${language}" xml:lang="${language}" dir="${direction}"><head><title>${xml(chapter.title)}</title><link rel="stylesheet" type="text/css" href="../styles/book.css"/></head><body dir="${direction}"><h1>${xml(chapter.title)}</h1>${paragraphs(chapter.content, language)}</body></html>`,
    })),
  ];
  return createZip(entries);
}

export function buildDocx(input) {
  const project = requireValid(input);
  const rtl = project.language === "ar";
  const author = xml(project.author.trim());
  const body = project.chapters.map((chapter) => {
    const title = `<w:p><w:pPr><w:pStyle w:val="Heading1"/>${rtl ? "<w:bidi/>" : ""}</w:pPr><w:r><w:t xml:space="preserve">${xml(chapter.title)}</w:t></w:r></w:p>`;
    const content = String(chapter.content).split(/\r?\n/).map((line) =>
      `<w:p><w:pPr>${rtl ? "<w:bidi/><w:jc w:val=\"right\"/>" : "<w:jc w:val=\"left\"/>"}</w:pPr><w:r><w:t xml:space="preserve">${xml(line)}</w:t></w:r></w:p>`
    ).join("");
    return title + content;
  }).join("");
  const document = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:pPr><w:pStyle w:val="Title"/>${rtl ? "<w:bidi/>" : ""}</w:pPr><w:r><w:t>${xml(project.title)}</w:t></w:r></w:p><w:p><w:pPr><w:jc w:val="center"/>${rtl ? "<w:bidi/>" : ""}</w:pPr><w:r><w:t>${author}</w:t></w:r></w:p>${body}<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr></w:body></w:document>`;
  const styles = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="Georgia" w:hAnsi="Georgia" w:eastAsia="Georgia" w:cs="Arial"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:pPr><w:jc w:val="center"/></w:pPr><w:rPr><w:b/><w:sz w:val="36"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:pPr><w:pageBreakBefore/><w:keepNext/></w:pPr><w:rPr><w:b/><w:sz w:val="30"/></w:rPr></w:style></w:styles>`;
  return createZip([
    { name: "[Content_Types].xml", data: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>' },
    { name: "_rels/.rels", data: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>' },
    { name: "word/document.xml", data: document },
    { name: "word/styles.xml", data: styles },
    { name: "word/_rels/document.xml.rels", data: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"></Relationships>' },
  ]);
}

export function decodeUtf8(data) { return decoder.decode(data); }
