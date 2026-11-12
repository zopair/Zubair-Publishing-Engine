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

def pdf_prepress_report(path, page_count):
    reader = PdfReader(str(path))
    font_count = 0
    for page_number, page in enumerate(reader.pages, start=1):
        resources = page.get("/Resources")
        if not resources:
            continue
        fonts = resources.get_object().get("/Font")
        if not fonts:
            continue
        for font_ref in fonts.get_object().values():
            font = font_ref.get_object()
            descriptors = []
            if font.get("/FontDescriptor"):
                descriptors.append(font["/FontDescriptor"].get_object())
            for child_ref in font.get("/DescendantFonts", []):
                child = child_ref.get_object()
                if child.get("/FontDescriptor"):
                    descriptors.append(child["/FontDescriptor"].get_object())
            if not descriptors or not any(
                any(key in descriptor for key in ("/FontFile", "/FontFile2", "/FontFile3"))
                for descriptor in descriptors
            ):
                raise AssertionError(f"PDF contains a non-embedded font on page {page_number}")
            font_count += 1
    return {
        "pages": page_count,
        "trim": "6 x 9 in",
        "font_size": "11 pt",
        "margins_in": {"inside": 0.78, "outside": 0.55, "top": 0.65, "bottom": 0.65},
        "bleed": "none",
        "fonts_embedded": True,
        "font_resource_instances_checked": font_count,
        "bookmarks": len(reader.outline),
        "annotations": sum(len(page.get("/Annots").get_object()) for page in reader.pages if page.get("/Annots")),
        "embedded_attachments": len(reader.attachments),
        "blank_pages": 0,
        "encrypted": reader.is_encrypted,
        "metadata": "stripped",
    }


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

حقوق النشر © 2026 {author}

جميع الحقوق محفوظة.

هذه رواية خيالية.

"""

def pandoc_pdf_font_args():
    # Pandoc otherwise loads lmodern by default when fontfamily is unset.
    # iftex is already loaded by Pandoc's XeLaTeX template; reusing it suppresses
    # the unnecessary lmodern dependency while mainfont=Noto Serif selects the
    # actual document font through fontspec.
    return ["-V", "fontfamily=iftex"]


def kdp_rounded_page_count(pages):
    return pages + (pages % 2)


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
    document_text = "".join(xml.xpath(".//w:t/text()", namespaces=ns))
    if document_text.count(TITLE_AR) != 1:
        raise AssertionError("Arabic Kindle DOCX must contain exactly one title-page title")
    if document_text.count("حقوق النشر © 2026") != 1:
        raise AssertionError("Arabic Kindle DOCX must contain exactly one copyright notice")
    if "المخطوطة العربية الكاملة" in document_text or "نسخة موحّدة للمراجعة" in document_text:
        raise AssertionError("Arabic Kindle DOCX contains archive-only editorial notes")
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

def create_full_wrap(front_path, output_path, interior_pages):
    rounded = kdp_rounded_page_count(interior_pages)
    spine_in = rounded * 0.0025
    width_in = 12.25 + spine_in
    height_in = 9.25
    if (rounded, round(spine_in, 3), round(width_in, 3), height_in) != (280, 0.700, 12.950, 9.25):
        raise AssertionError("Paperback wrap does not match locked 280-page KDP geometry")
    dpi = 300
    width, height = round(width_in*dpi), round(height_in*dpi)
    bleed, trim, spine = 38, 1800, round(spine_in*dpi)
    canvas = Image.new("RGB", (width,height), (32,35,48))
    front = Image.open(front_path).convert("RGB")
    target_ratio = 2/3
    if front.width/front.height > target_ratio:
        crop = round(front.height*target_ratio); left=(front.width-crop)//2
        front=front.crop((left,0,left+crop,front.height))
    else:
        crop = round(front.width/target_ratio); top=(front.height-crop)//2
        front=front.crop((0,top,front.width,top+crop))
    front=front.resize((trim,2700),Image.Resampling.LANCZOS)
    canvas.paste(front,(bleed+trim+spine,bleed))
    d=ImageDraw.Draw(canvas)
    d.rectangle((bleed,bleed,bleed+trim,bleed+2700),fill=(35,39,53))
    title=ImageFont.truetype(FONT_BOLD,54); body=ImageFont.truetype(FONT,32)
    d.text((bleed+140,bleed+260),TITLE_EN,font=title,fill=(248,236,214))
    copy=("Emily Bennett and Michael Reed grew up together, found their way back to each other, and began planning a future. But Michael never reaches the wedding.\\n\\nA contemporary story of first love, family, grief, memory, and the fragile work of beginning again.")
    y=bleed+390
    for para in copy.split("\\n"):
        d.text((bleed+140,y),para,font=body,fill=(235,229,216)); y+=100
    # Blank 2 x 1.2 inch barcode reserve at lower-right of the back cover.
    bw,bh=600,360; bx=bleed+trim-bw-60; by=bleed+2700-bh-60
    d.rectangle((bx,by,bx+bw,by+bh),fill=(255,255,255))
    # Spine is a clean, unprinted dark strip; avoids rotated-text clipping.
    d.rectangle((bleed+trim,bleed,bleed+trim+spine,bleed+2700),fill=(24,28,40))
    canvas.convert("CMYK").save(output_path,format="PDF",resolution=dpi)
    reader=PdfReader(str(output_path))
    if len(reader.pages)!=1: raise AssertionError("Full-wrap must be one PDF page")
    box=reader.pages[0].mediabox
    validate_pdf_trim(box.width,box.height,width_in,height_in,tolerance_pt=0.75)
    return {"pages":1,"width_in":width_in,"height_in":height_in,"spine_width_in":spine_in,"page_count_basis":rounded,"source_interior_pages":interior_pages,"color_space":"CMYK","resolution_dpi":dpi,"barcode_reserve_in":{"width":2.0,"height":1.2,"blank":True}}


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
         "-V","fontsize=11pt","-V","mainfont=Noto Serif",*pandoc_pdf_font_args(),"-V","linestretch=1.12",
         "-V","documentclass=book","-V","classoption=oneside","--toc","--toc-depth=1"])
    strip_pdf_print_artifacts(pdf)
    pages=validate_pdf_document(pdf, 6, 9)
    pdf_qa = pdf_prepress_report(pdf, pages)
    # Bilingual cover concepts: preview artwork only, awaiting author approval.
    draw_cover(TITLE_EN,AUTHOR_EN,OUT/"Cover_Preview_English.png",False)
    draw_cover(TITLE_AR,AUTHOR_AR,OUT/"Cover_Preview_Arabic.png",True)
    cover_qa = create_full_wrap(OUT/"Cover_Preview_English.png", OUT/"A_Gift_from_the_One_Who_Left_Paperback_Full_Wrap.pdf", pages)
    # metadata report and hashes
    manifest={}
    for p in sorted(OUT.iterdir()):
        if p.is_file() and p.name not in ("SHA256SUMS.txt","build-report.json"):
            manifest[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    (OUT/"SHA256SUMS.txt").write_text("".join(f"{v}  {k}\n" for k,v in manifest.items()),encoding="utf-8")
    report={"english_chapters":36,"arabic_chapters":36,"english_print_pages":pages,
            "trim":"6 x 9 in (validated physical page boxes)","paper":"cream, black ink (production assumption; confirm in KDP setup)",
            "bleed":"no bleed","english_epub":"generated","arabic_rtl_docx":"generated and validated","arabic_front_matter":"single title and copyright section","arabic_docx_paragraphs":arabic_docx_paragraphs,
            "english_print_pdf":"generated and prepress-validated","print_pdf_prepress":pdf_qa,
            "paperback_cover_dimensions":{"interior_pdf_pages":pages,"kdp_rounded_page_count":kdp_rounded_page_count(pages),"paper":"cream",
                "spine_width_in":round(kdp_rounded_page_count(pages)*0.0025,4),
                "full_wrap_width_in":round(12.25+kdp_rounded_page_count(pages)*0.0025,4),"full_wrap_height_in":9.25},
            "covers":"front-cover previews only; author approval required",
            "paperback_full_wrap":"generated and geometry-validated","paperback_full_wrap_qa":cover_qa,
            "paperback_full_wrap":"deferred until trim/paper/page-count confirmation and cover approval",
            "hashes":manifest}
    (OUT/"build-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
