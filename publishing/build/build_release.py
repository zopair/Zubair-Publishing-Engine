#!/usr/bin/env python3
"""Deterministic prepress builder for A Gift from the One Who Left."""
from pathlib import Path
import re, hashlib, json, subprocess, sys, zipfile, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pypdf import PdfReader, PdfWriter
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "publishing" / "release-candidate"
OUT.mkdir(parents=True, exist_ok=True)
EN = ROOT / "manuscript/en/FULL-ENGLISH-MANUSCRIPT.md"
AR = ROOT / "manuscript/ar/FULL-ARABIC-MANUSCRIPT.md"
TITLE_EN = "A Gift from the One Who Left"
TITLE_AR = "هدية من الغائب"
AUTHOR_EN = "Aly HUSSEIN FEKRY"
AUTHOR_AR = "على حسين فكرى"
FONT = "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
FONT_AR = "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf"
FONT_AR_BOLD = "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Bold.ttf"

def run(cmd):
    subprocess.run(cmd, check=True)

def source_text(path):
    text = path.read_text(encoding="utf-8")
    text = re.split(r"^## (?:Digital Integrity Fingerprint|البصمة الرقمية لسلامة النص)\s*$", text, flags=re.M)[0]
    return text

def prepare_arabic_body(text):
    # The archive master includes its own review title and copyright block.
    # The KDP builder supplies a clean, single front-matter section, so retain
    # only the story body beginning with Chapter 1.
    marker = "# الفصل الأول"
    start = text.find(marker)
    if start < 0:
        raise AssertionError("Arabic KDP body must contain Chapter 1")
    body = text[start:].lstrip()
    if "المخطوطة العربية الكاملة" in body or "نسخة موحّدة للمراجعة" in body:
        raise AssertionError("Arabic KDP body contains archive-only editorial front matter")
    if "حقوق النشر © 2026" in body:
        raise AssertionError("Arabic KDP body contains a duplicate copyright section")
    return body


def assert_master(text, arabic=False):
    pat = r"^# Chapter\s+\d+" if not arabic else r"^# الفصل\s+[اأإآ\d]+"
    chapters = re.findall(pat, text, flags=re.M)
    assert len(chapters) == 36, f"Expected 36 chapters, got {len(chapters)}"
    ep = r"^## Epilogue|^# Epilogue" if not arabic else r"^## الخاتمة|^# الخاتمة"
    assert len(re.findall(ep, text, flags=re.M)) == 1, "Expected exactly one epilogue"
    if not arabic:
        # Validate the established story event in its narrative context, not by
        # requiring a brittle sentence that need not appear verbatim.
        chapter31 = re.search(r"^# Chapter 31\b(.*?)(?=^# Chapter 32\b)", text, flags=re.M | re.S)
        assert chapter31, "Chapter 31 is required for wedding-loss validation"
        chapter31_text = chapter31.group(1).lower()
        assert "no morning after the wedding" in chapter31_text, (
            "Chapter 31 must establish that the wedding never took place"
        )
        assert "funeral was held" in chapter31_text, (
            "Chapter 31 must establish Michael's death and its aftermath"
        )
        after_chapter30 = text.lower().split("# chapter 31",1)[-1]
        assert "honeymoon" not in after_chapter30, "Obsolete honeymoon text found after Chapter 30"
    else:
        assert "على حسين فكرى" in text
    return len(chapters)

def frontmatter(title, author, lang):
    if lang == "en":
        return f"""---
title: "{title}"
author: "{author}"
lang: en
---

# {title}

**{author}**

Copyright © 2026 {author}

All rights reserved.

This is a work of fiction.

"""
    return f"""---
title: "{title}"
author: "{author}"
lang: ar
---

# {title}

**{author}**

حقوق النشر © 2026 {author}

جميع الحقوق محفوظة.

هذه رواية خيالية.

"""

def validate_pdf_trim(width_pt, height_pt, expected_width_in, expected_height_in, tolerance_pt=0.5):
    expected_width_pt = expected_width_in * 72
    expected_height_pt = expected_height_in * 72
    if abs(float(width_pt) - expected_width_pt) > tolerance_pt or abs(float(height_pt) - expected_height_pt) > tolerance_pt:
        raise AssertionError(
            f"PDF page size must be {expected_width_in} x {expected_height_in} in "
            f"({expected_width_pt:.1f} x {expected_height_pt:.1f} pt); "
            f"found {float(width_pt)/72:.3f} x {float(height_pt)/72:.3f} in"
        )


def strip_pdf_print_artifacts(path):
    reader = PdfReader(str(path))
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    root = writer._root_object
    for key in ("/Outlines", "/Names", "/AF", "/OpenAction", "/PageMode", "/Metadata", "/AcroForm"):
        root.pop(key, None)
    for page in writer.pages:
        page.pop("/Annots", None)
    try:
        writer._info.get_object().clear()
    except Exception:
        pass
    cleaned = Path(str(path) + ".clean")
    with cleaned.open("wb") as stream:
        writer.write(stream)
    cleaned.replace(path)


def validate_pdf_document(path, expected_width_in=6, expected_height_in=9):
    reader = PdfReader(str(path))
    if not reader.pages:
        raise AssertionError("PDF contains no pages")
    if reader.outline:
        raise AssertionError("PDF contains bookmarks/outlines")
    if reader.attachments:
        raise AssertionError("PDF contains embedded attachments")
    root = reader.trailer["/Root"].get_object()
    if root.get("/Names") or root.get("/AF") or root.get("/Metadata"):
        raise AssertionError("PDF contains named destinations, associated files, or XMP metadata")
    for index, page in enumerate(reader.pages, start=1):
        if page.get("/Annots"):
            raise AssertionError(f"PDF contains annotations on page {index}")
        box = page.mediabox
        try:
            validate_pdf_trim(box.width, box.height, expected_width_in, expected_height_in)
        except AssertionError as exc:
            raise AssertionError(f"PDF page size validation failed on page {index}: {exc}") from exc
        page_text = (page.extract_text() or "").strip()
        if not page_text or re.fullmatch(r"(?:[0-9]+|[ivxlcdm]+)", page_text, flags=re.I):
            raise AssertionError(f"PDF contains a blank or page-number-only page at page {index}")
    return len(reader.pages)


def make_arabic_docx(md_path, target):
    # Pandoc preserves Markdown structure; post-process OOXML for true RTL paragraph/run direction.
    run(["pandoc", str(md_path), "-o", str(target), "--from=markdown"])
    with zipfile.ZipFile(target, "r") as zin:
        files = {n: zin.read(n) for n in zin.namelist()}
    from lxml import etree
    xml = etree.fromstring(files["word/document.xml"])
    ns = {"w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    for p in xml.xpath(".//w:p", namespaces=ns):
        ppr = p.find("{%s}pPr" % ns["w"])
        if ppr is None:
            ppr = etree.Element("{%s}pPr" % ns["w"]); p.insert(0,ppr)
        bidi = ppr.find("{%s}bidi" % ns["w"])
        if bidi is None: bidi = etree.SubElement(ppr,"{%s}bidi" % ns["w"])
        bidi.set("{%s}val" % ns["w"],"1")
        style = ppr.find("{%s}pStyle" % ns["w"])
        if style is not None and style.get("{%s}val" % ns["w"]) == "BodyText":
            ind = ppr.find("{%s}ind" % ns["w"])
            if ind is None: ind = etree.SubElement(ppr,"{%s}ind" % ns["w"])
            ind.set("{%s}firstLine" % ns["w"],"288")  # KDP Arabic guidance: 0.2 in
        jc = ppr.find("{%s}jc" % ns["w"])
        if jc is None: jc = etree.SubElement(ppr,"{%s}jc" % ns["w"])
        jc.set("{%s}val" % ns["w"],"right")
        for r in p.findall(".//{%s}r" % ns["w"]):
            rpr = r.find("{%s}rPr" % ns["w"])
            if rpr is None: rpr = etree.Element("{%s}rPr" % ns["w"]); r.insert(0,rpr)
            rtl = rpr.find("{%s}rtl" % ns["w"])
            if rtl is None: rtl = etree.SubElement(rpr,"{%s}rtl" % ns["w"])
            rtl.set("{%s}val" % ns["w"],"1")
            lang = rpr.find("{%s}lang" % ns["w"])
            if lang is None: lang = etree.SubElement(rpr,"{%s}lang" % ns["w"])
            lang.set("{%s}val" % ns["w"],"ar")
            lang.set("{%s}bidi" % ns["w"],"ar")
            rf = rpr.find("{%s}rFonts" % ns["w"])
            if rf is None: rf = etree.SubElement(rpr,"{%s}rFonts" % ns["w"])
            rf.set("{%s}ascii" % ns["w"],"Noto Naskh Arabic")
            rf.set("{%s}hAnsi" % ns["w"],"Noto Naskh Arabic")
            rf.set("{%s}cs" % ns["w"],"Noto Naskh Arabic")
    files["word/document.xml"] = etree.tostring(xml, xml_declaration=True, encoding="UTF-8", standalone=True)
    with zipfile.ZipFile(target,"w",zipfile.ZIP_DEFLATED) as zout:
        for n,b in files.items(): zout.writestr(n,b)
    doc = Document(target)
    doc.core_properties.language = "ar"
    doc.save(target)


def validate_arabic_docx(path):
    with zipfile.ZipFile(path, "r") as z:
        from lxml import etree
        xml = etree.fromstring(z.read("word/document.xml"))
    ns = {"w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs = xml.xpath(".//w:body/w:p", namespaces=ns)
    if not paragraphs:
        raise AssertionError("Arabic DOCX contains no paragraphs")
    missing_rtl = [i for i,p in enumerate(paragraphs,1) if not p.xpath("./w:pPr/w:bidi[@w:val='1']", namespaces=ns)]
    if missing_rtl:
        raise AssertionError(f"Arabic DOCX paragraphs missing RTL direction: {missing_rtl[:10]}")
    missing_indent = [i for i,p in enumerate(paragraphs,1)
        if p.xpath("./w:pPr/w:pStyle[@w:val='BodyText']", namespaces=ns)
        and not p.xpath("./w:pPr/w:ind[@w:firstLine='288']", namespaces=ns)]
    if missing_indent:
        raise AssertionError(f"Arabic body paragraphs missing 0.2in first-line indent: {missing_indent[:10]}")
    missing_run_rtl = len(xml.xpath(".//w:r[.//w:t and not(w:rPr/w:rtl[@w:val='1'])]", namespaces=ns))
    if missing_run_rtl:
        raise AssertionError(f"Arabic DOCX contains {missing_run_rtl} text runs without RTL run direction")
    return len(paragraphs)


def draw_cover(title, author, out, arabic=False):
    W,H=1600,2560
    im=Image.new("RGB",(W,H),(30,29,39)); px=im.load()
    # restrained dusk gradient
    top=(39,43,60); bottom=(18,24,35)
    for y in range(H):
        t=y/H
        c=tuple(int(top[i]*(1-t)+bottom[i]*t) for i in range(3))
        for x in range(W): px[x,y]=c
    d=ImageDraw.Draw(im,"RGBA")
    # warm shaft of light and subtle bokeh
    glow=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glow)
    gd.ellipse((250,500,1500,1700),fill=(224,164,104,80))
    glow=glow.filter(ImageFilter.GaussianBlur(180)); im=Image.alpha_composite(im.convert("RGBA"),glow)
    d=ImageDraw.Draw(im,"RGBA")
    for x,y,r,a in [(250,620,18,50),(1280,520,22,45),(1420,950,14,35),(300,1200,12,30),(1200,1450,24,35)]:
        d.ellipse((x-r,y-r,x+r,y+r),fill=(255,220,170,a))
    # wooden keepsake box, no people, no wedding imagery
    bx,by,bw,bh=250,1120,1100,820
    d.rounded_rectangle((bx,by,bx+bw,by+bh),radius=44,fill=(91,55,42,255),outline=(196,150,99,255),width=12)
    d.rounded_rectangle((bx+45,by+55,bx+bw-45,by+bh-50),radius=24,fill=(45,35,35,255),outline=(145,103,70,255),width=7)
    # photographs inside the box: abstract scenery only
    for i,(x,y,ang) in enumerate([(400,1260,-5),(760,1220,6),(580,1510,2)]):
        card=Image.new("RGBA",(300,380),(236,224,199,255)); cd=ImageDraw.Draw(card)
        cd.rectangle((15,15,285,300),fill=(83+i*9,102+i*5,115+i*3,255))
        cd.ellipse((45,55,260,260),fill=(206,155,111,255))
        cd.rectangle((15,305,285,365),fill=(242,232,211,255))
        card=card.rotate(ang,expand=True,resample=Image.Resampling.BICUBIC)
        im.alpha_composite(card,(x,y))
    d=ImageDraw.Draw(im,"RGBA")
    # small paper tag and ribbon, deliberately no rings
    d.polygon([(1120,1600),(1340,1560),(1380,1810),(1150,1840)],fill=(225,211,184,255))
    d.line((1140,1625,1340,1595),fill=(145,105,72,255),width=5)
    d.ellipse((1295,1740,1330,1775),outline=(145,105,72,255),width=5)
    # title typography in reserved upper region
    if arabic:
        from arabic_reshaper import reshape
        from bidi.algorithm import get_display
        title_text=get_display(reshape(title))
        author_text=get_display(reshape(author))
        tf=ImageFont.truetype(FONT_AR_BOLD,118)
        af=ImageFont.truetype(FONT_AR,64)
        d.text((W//2,350),title_text,font=tf,fill=(248,236,214,255),anchor="mm",direction="rtl",language="ar")
        d.text((W//2,560),author_text,font=af,fill=(219,180,125,255),anchor="mm",direction="rtl",language="ar")
    else:
        tf=ImageFont.truetype(FONT_BOLD,108)
        af=ImageFont.truetype(FONT,62)
        lines=title.split(" ")
        chunks=["A Gift from the","One Who Left"]
        for j,line in enumerate(chunks):
            d.text((W//2,340+j*135),line,font=tf,fill=(248,236,214,255),anchor="mm")
        d.text((W//2,690),author,font=af,fill=(219,180,125,255),anchor="mm")
    # restrained subtitle
    sf=ImageFont.truetype(FONT,48)
    d.text((W//2,900),"Some memories refuse to say goodbye" if not arabic else "بعض الذكريات ترفض الوداع",font=sf,fill=(230,213,185,255),anchor="mm")
    # small border
    d.rounded_rectangle((75,75,W-75,H-75),radius=22,outline=(197,155,108,150),width=4)
    im.convert("RGB").save(out,quality=95)

def main():
    en=source_text(EN); ar=source_text(AR)
    assert_master(en,False); assert_master(ar,True)
    # English Kindle reflowable EPUB
    enmd=OUT/"english-kindle-source.md"
    enmd.write_text(frontmatter(TITLE_EN,AUTHOR_EN,"en")+en,encoding="utf-8")
    run(["pandoc",str(enmd),"-o",str(OUT/"A_Gift_from_the_One_Who_Left_Kindle.epub"),
         "--toc","--toc-depth=1","--split-level=1","--metadata=lang:en",
         "--metadata=title:"+TITLE_EN,"--metadata=author:"+AUTHOR_EN])
    # Arabic Kindle DOCX, explicitly patched to RTL
    armd=OUT/"arabic-kindle-source.md"
    ar_body = prepare_arabic_body(ar)
    armd.write_text(frontmatter(TITLE_AR,AUTHOR_AR,"ar")+ar_body,encoding="utf-8")
    make_arabic_docx(armd,OUT/"هدية_من_الغائب_Kindle_RTL.docx")
    arabic_docx_paragraphs = validate_arabic_docx(OUT/"هدية_من_الغائب_Kindle_RTL.docx")
    # English print interior: 6x9 in, black ink, cream paper assumption, no bleed.
    pdf=OUT/"A_Gift_from_the_One_Who_Left_Paperback_Interior_6x9.pdf"
    run(["pandoc",str(enmd),"-o",str(pdf),"--pdf-engine=xelatex",
         "-V","geometry:paperwidth=6in","-V","geometry:paperheight=9in",
         "-V","geometry:inner=0.78in","-V","geometry:outer=0.55in",
         "-V","geometry:top=0.65in","-V","geometry:bottom=0.65in",
         "-V","fontsize=11pt","-V","mainfont=Noto Serif","-V","linestretch=1.12",
         "-V","documentclass=book","-V","classoption=oneside","--toc","--toc-depth=1"])
    strip_pdf_print_artifacts(pdf)
    pages=validate_pdf_document(pdf, 6, 9)
    # Bilingual cover concepts: preview artwork only, awaiting author approval.
    draw_cover(TITLE_EN,AUTHOR_EN,OUT/"Cover_Preview_English.png",False)
    draw_cover(TITLE_AR,AUTHOR_AR,OUT/"Cover_Preview_Arabic.png",True)
    # metadata report and hashes
    manifest={}
    for p in sorted(OUT.iterdir()):
        if p.is_file() and p.name not in ("SHA256SUMS.txt","build-report.json"):
            manifest[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    (OUT/"SHA256SUMS.txt").write_text("".join(f"{v}  {k}\n" for k,v in manifest.items()),encoding="utf-8")
    report={"english_chapters":36,"arabic_chapters":36,"english_print_pages":pages,
            "trim":"6 x 9 in (validated physical page boxes)","paper":"cream, black ink (production assumption; confirm in KDP setup)",
            "bleed":"no bleed","english_epub":"generated","arabic_rtl_docx":"generated and validated","arabic_front_matter":"single title and copyright section","arabic_docx_paragraphs":arabic_docx_paragraphs,
            "english_print_pdf":"generated","covers":"preview only; approval required",
            "paperback_full_wrap":"deferred until trim/paper/page-count confirmation and cover approval",
            "hashes":manifest}
    (OUT/"build-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
