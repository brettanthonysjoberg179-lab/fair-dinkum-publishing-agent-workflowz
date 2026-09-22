#!/usr/bin/env python3
"""Fair Dinkum Publishing — ebook PDF + flipbook builder (reportlab, A4).
Usage: python3 build_ebook_pdf.py [skate|graffiti|all]

Two correct formats, not one compromised file:
  PAGINATED PDF (02-ebook.pdf) — print-style pagination:
    cover (no folio) → front matter (roman i, ii…) → body (arabic 1, 2…),
    chapters open on fresh pages, running heads (title verso / chapter recto),
    opener pages carry a small centred folio, dot-leader TOC with page numbers.
  PAGELESS flipbook (01-flipbook.html) — reflowable single-file reader, no folios.
"""
import os, re, sys, glob

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (Paragraph, Spacer, PageBreak, ListFlowable, ListItem,
                                HRFlowable, NextPageTemplate, BaseDocTemplate, PageTemplate, Frame)
from reportlab.platypus.tableofcontents import TableOfContents

PRIMARY = HexColor('#0E4D2E')   # deep eucalypt green
ACCENT = HexColor('#C88A00')    # wattle gold
DARK = HexColor('#1e293b')
GRAY = HexColor('#64748b')
LIGHT = HexColor('#f8fafc')

BOOKS = {
    'playbook': {
        'src': 'book/aussie-agent-playbook',
        'out': 'digital_product_workforce/outputs/prod-fairdinkum-ebook-001/build',
        'title': 'Aussie Agent Workflowz: Fair Dinkum AI Side-Hustle Playbook',
        'subtitle': 'From Red Dust to Passive Income — 12 Agent Workflows',
        'prod': 'FDP-AAW-001',
    },
    'solo': {
        'src': 'book/solopreneurs-os',
        'out': 'digital_product_workforce/outputs/prod-fairdinkum-ebook-002/build',
        'title': 'Solopreneur OS: The Fair Dinkum Solo Business System',
        'subtitle': 'From Chaos to Calm — One Inbox, One Review, One Money Day',
        'prod': 'FDP-SOLO-002',
    },
    'skate': {
        'src': 'book/the-history-of-skateboarding',
        'out': 'digital_product_workforce/outputs/prod-fairdinkum-ebook-003/build',
        'title': 'The History of Skateboarding',
        'subtitle': 'A Fair Dinkum Ride — From Footpaths to Tokyo 2020',
        'prod': 'FDP-SKATE-003',
    },
    'graffiti': {
        'src': 'book/the-history-of-graffiti',
        'out': 'digital_product_workforce/outputs/prod-fairdinkum-ebook-004/build',
        'title': 'The History of Graffiti',
        'subtitle': 'Walls That Talk — From Ancient Echoes to the Internet Age',
        'prod': 'FDP-GRAF-004',
    },
}

# ---------------------------------------------------------------- styles ---

def styles():
    base = getSampleStyleSheet()
    return {
        'cover_title': ParagraphStyle('CT', parent=base['Title'], fontSize=34, leading=40,
                                      textColor=PRIMARY, alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=12),
        'cover_sub': ParagraphStyle('CS', parent=base['Normal'], fontSize=14, leading=20,
                                    textColor=GRAY, alignment=TA_CENTER, spaceAfter=6),
        'brand': ParagraphStyle('BR', parent=base['Normal'], fontSize=11, leading=15,
                                textColor=ACCENT, alignment=TA_CENTER, fontName='Helvetica-Bold', spaceBefore=24),
        'h1': ParagraphStyle('H1', parent=base['Heading1'], fontSize=22, leading=28,
                             textColor=PRIMARY, fontName='Helvetica-Bold', spaceBefore=0, spaceAfter=10,
                             keepWithNext=True),
        'h2': ParagraphStyle('H2', parent=base['Heading2'], fontSize=15, leading=21,
                             textColor=DARK, fontName='Helvetica-Bold', spaceBefore=16, spaceAfter=6, keepWithNext=True),
        'h3': ParagraphStyle('H3', parent=base['Heading3'], fontSize=12, leading=17,
                             textColor=GRAY, fontName='Helvetica-BoldOblique', spaceBefore=12, spaceAfter=4),
        'body': ParagraphStyle('BO', parent=base['Normal'], fontSize=10.5, leading=16,
                               textColor=DARK, alignment=TA_JUSTIFY, spaceAfter=7),
        'bullet': ParagraphStyle('BU', parent=base['Normal'], fontSize=10.5, leading=16,
                                 textColor=DARK, leftIndent=18, spaceAfter=4),
        'quote': ParagraphStyle('QU', parent=base['Normal'], fontSize=10.5, leading=16,
                                textColor=GRAY, leftIndent=16, spaceAfter=7, fontName='Helvetica-Oblique',
                                borderPadding=(6, 6, 6), backColor=LIGHT),
        'caption': ParagraphStyle('CA', parent=base['Normal'], fontSize=9, leading=13,
                                  textColor=GRAY, alignment=TA_CENTER, spaceAfter=10),
        'toc0': ParagraphStyle('T0', parent=base['Normal'], fontSize=12, leading=20,
                               textColor=DARK, fontName='Helvetica-Bold', leftIndent=0),
        'toc1': ParagraphStyle('T1', parent=base['Normal'], fontSize=10, leading=16,
                               textColor=GRAY, leftIndent=18),
    }

def footer(canvas, doc):
    """Legacy simple footer — kept for build_samples.py (teasers)."""
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(GRAY)
    canvas.drawCentredString(A4[0] / 2, 15 * mm,
        f"Fair Dinkum Publishing · ABN 63 590 716 023 · {getattr(doc, 'fdp_title', '')} · p. {doc.page}")
    canvas.restoreState()

# ------------------------------------------------------------ markdown ---

def md_inline(t):
    t = t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', t)
    t = re.sub(r'`(.+?)`', r'<font face="Courier">\1</font>', t)
    t = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', t)
    return t

def md_to_flowables(path, st):
    with open(path) as f:
        lines = f.read().split('\n')
    out, buf, bullets = [], [], []

    def flush_para():
        if buf:
            out.append(Paragraph(md_inline(' '.join(buf)), st['body']))
            buf.clear()

    def flush_bullets(ordered=False):
        if bullets:
            items = [ListItem(Paragraph(md_inline(b), st['bullet']), leftIndent=18) for b in bullets]
            out.append(ListFlowable(items, bulletType='1' if ordered else 'bullet', start='1'))
            bullets.clear()

    for ln in lines:
        s = ln.strip()
        if not s:
            flush_para(); flush_bullets(); continue
        if s.startswith('```'):
            flush_para(); continue
        if s.startswith('# '):
            flush_para(); flush_bullets(); out.append(Paragraph(md_inline(s[2:]), st['h1'])); continue
        if s.startswith('## '):
            flush_para(); flush_bullets(); out.append(Paragraph(md_inline(s[3:]), st['h2'])); continue
        if s.startswith('### '):
            flush_para(); flush_bullets(); out.append(Paragraph(md_inline(s[4:]), st['h3'])); continue
        if s.startswith('---') or s == '***':
            flush_para(); flush_bullets(); out.append(HRFlowable(width='100%', color=GRAY)); continue
        if s.startswith('>'):
            flush_para(); flush_bullets(); out.append(Paragraph(md_inline(s.lstrip('> ')), st['quote'])); continue
        m = re.match(r'^(\d+)[.)]\s+(.*)', s)
        if m:
            flush_para(); bullets.append(m.group(2)); continue
        if s.startswith(('- ', '* ')):
            flush_para(); bullets.append(s[2:]); continue
        if s.startswith('|'):
            continue  # tables kept in flipbook HTML only
        buf.append(s)
    flush_para(); flush_bullets()
    return out

def chapter_title_of(path):
    with open(path) as f:
        for ln in f.read().split('\n'):
            if ln.startswith('# '):
                return ln[2:].strip()
    return os.path.basename(path)

# ------------------------------------------------- paginated document ---

def _roman(n):
    table = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'),
             (90, 'XC'), (50, 'L'), (40, 'XL'), (10, 'X'), (9, 'IX'),
             (5, 'V'), (4, 'IV'), (1, 'I')]
    out = ''
    for v, s in table:
        while n >= v:
            out += s
            n -= v
    return out.lower()

class FDPDoc(BaseDocTemplate):
    """Cover (no folio) → front matter (roman) → body (arabic, running heads)."""

    def __init__(self, filename, title, chapters, **kw):
        super().__init__(filename, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                         topMargin=22 * mm, bottomMargin=20 * mm,
                         title=title, author='Fair Dinkum Publishing', **kw)
        self.fdp_title = title
        self._chapter_titles = set(chapters)
        self._cur_chapter = ''
        self._body_start = None  # physical page where arabic p.1 begins
        fw, fh = self.width, self.height
        frame = Frame(self.leftMargin, self.bottomMargin, fw, fh, id='main')
        self.addPageTemplates([
            PageTemplate(id='Cover', frames=[frame], onPage=self._cover_page),
            PageTemplate(id='Front', frames=[frame], onPage=self._front_page),
            PageTemplate(id='Body', frames=[frame], onPage=self._body_page),
            PageTemplate(id='Chapter', frames=[frame], onPage=self._chapter_page),
        ])

    # -- folio helpers --
    def _arabic(self):
        return self.page - (self._body_start or self.page) + 1

    def _paint_folio_outer(self, canvas, num):
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(GRAY)
        y = 15 * mm
        if canvas.getPageNumber() % 2 == 0:
            canvas.drawString(18 * mm, y, str(num))            # verso: left
        else:
            canvas.drawRightString(A4[0] - 18 * mm, y, str(num))  # recto: right

    def _paint_head(self, canvas, text, even_left=True):
        canvas.setFont('Helvetica', 7.5)
        canvas.setFillColor(GRAY)
        y = A4[1] - 14 * mm
        if canvas.getPageNumber() % 2 == 0:
            canvas.drawString(18 * mm, y, text[:80])
        else:
            canvas.drawRightString(A4[0] - 18 * mm, y, text[:80])
        canvas.setStrokeColor(LIGHT)
        canvas.setLineWidth(0.5)
        canvas.line(18 * mm, y - 3, A4[0] - 18 * mm, y - 3)

    # -- page templates --
    def _cover_page(self, canvas, doc):
        pass  # clean cover, no folio

    def _front_page(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(GRAY)
        canvas.drawCentredString(A4[0] / 2, 15 * mm, _roman(canvas.getPageNumber() - 1))
        canvas.restoreState()

    def _body_page(self, canvas, doc):
        canvas.saveState()
        head = self.fdp_title if canvas.getPageNumber() % 2 == 0 else (self._cur_chapter or self.fdp_title)
        self._paint_head(canvas, head)
        self._paint_folio_outer(canvas, self._arabic())
        canvas.restoreState()

    def _chapter_page(self, canvas, doc):
        canvas.saveState()  # opener: no running head, small centred folio
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(GRAY)
        canvas.drawCentredString(A4[0] / 2, 15 * mm, str(self._arabic()))
        canvas.restoreState()

    # -- TOC + chapter tracking --
    def afterFlowable(self, flowable):
        if not isinstance(flowable, Paragraph):
            return
        name, text = flowable.style.name, flowable.getPlainText()
        if name == 'H1' and text in self._chapter_titles:
            if self._body_start is None:
                self._body_start = self.page
            self._cur_chapter = text
            self.notify('TOCEntry', (0, text, self.page))
        elif name == 'H2' and self._body_start is not None:
            self.notify('TOCEntry', (1, text, self.page))

def build_pdf(key, cfg):
    st = styles()
    ch_files = sorted(glob.glob(os.path.join(cfg['src'], 'ch*.md')))
    assert ch_files, f"no chapters in {cfg['src']}"
    titles = [chapter_title_of(c) for c in ch_files]
    os.makedirs(cfg['out'], exist_ok=True)
    pdf = os.path.join(cfg['out'], '02-ebook.pdf')

    toc = TableOfContents()
    toc.levelStyles = [st['toc0'], st['toc1']]
    toc.dotsMinLevel = 0

    story = [
        # Cover (template Cover: no folio)
        Spacer(1, 60),
        Paragraph('FAIR DINKUM PUBLISHING', st['brand']),
        Spacer(1, 12),
        Paragraph(cfg['title'], st['cover_title']),
        Paragraph(cfg['subtitle'], st['cover_sub']),
        Spacer(1, 24),
        HRFlowable(width='30%', color=ACCENT, thickness=2, spaceAfter=24, hAlign='CENTER'),
        Paragraph(f"{cfg['prod']} · Flipbook + PDF Edition · 2026", st['caption']),
        Paragraph('Adelaide, South Australia', st['caption']),
        # Front matter (template Front: roman folios)
        NextPageTemplate('Front'), PageBreak(),
        Paragraph(cfg['title'], st['h1']),
        Paragraph(cfg['subtitle'], st['cover_sub']),
        Spacer(1, 12),
        Paragraph('© 2026 Fair Dinkum Publishing · All rights reserved.<br/>'
                  'ABN 63 590 716 023 · Adelaide, South Australia<br/>'
                  f"{cfg['prod']} · Flipbook + PDF Edition · 2026 · ISBN: TBD<br/><br/>"
                  'General information only — prices in AUD, GST-inclusive. '
                  'See ato.gov.au or your accountant for advice.', st['caption']),
        NextPageTemplate('Front'), PageBreak(),
        Paragraph('Contents', st['h1']),
        Paragraph('Chapters open on fresh pages; body pages carry running heads.', st['caption']),
        toc,
    ]
    for path, title in zip(ch_files, titles):
        story += [NextPageTemplate('Chapter'), PageBreak(),
                  NextPageTemplate('Body')]
        flows = md_to_flowables(path, st)
        # tag the chapter H1 (first H1 in file) — md_to_flowables already emits it
        story += flows
    story += [NextPageTemplate('Body'), PageBreak(),
              Paragraph('Glossary & Resources', st['h1']),
              Paragraph('Key terms, suppliers, and further reading live at fair-dinkum-book-hub. '
                        'Enjoyed this book? Leave a review — it keeps independent Aussie publishing alive.', st['body']),
              Spacer(1, 24),
              Paragraph('© 2026 Fair Dinkum Publishing · All rights reserved.', st['caption'])]

    doc = FDPDoc(pdf, cfg['title'], titles)
    doc.multiBuild(story)  # multi-pass: resolves TOC page numbers
    size = os.path.getsize(pdf)
    print(f"PDF {key}: {len(ch_files)} chapters, paginated (roman front + arabic body) → {pdf} ({size/1024:.0f} KB)")
    return pdf

# ------------------------------------------------- pageless flipbook ---

def build_flipbook(key, cfg):
    ch_files = sorted(glob.glob(os.path.join(cfg['src'], 'ch*.md')))
    parts = []
    for ch in ch_files:
        with open(ch) as f:
            txt = f.read()
        html = []
        for ln in txt.split('\n'):
            s = ln.strip()
            if s.startswith('### '): html.append(f"<h3>{s[4:]}</h3>")
            elif s.startswith('## '): html.append(f"<h2>{s[3:]}</h2>")
            elif s.startswith('# '): html.append(f"<h2 class='ch'>{s[2:]}</h2>")
            elif s.startswith(('- ', '* ')): html.append(f"<li>{s[2:]}</li>")
            elif s.startswith('>'): html.append(f"<blockquote>{s.lstrip('> ')}</blockquote>")
            elif not s: html.append('')
            else: html.append(f"<p>{s}</p>")
        parts.append('\n'.join(html))
    doc = f"""<!DOCTYPE html><html lang="en-AU"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{cfg['title']} — Fair Dinkum Publishing</title>
<style>body{{font-family:Georgia,serif;max-width:720px;margin:0 auto;padding:24px;color:#1e293b}}
.cover{{text-align:center;padding:48px 0}}.ch{{color:#0E4D2E;border-top:3px solid #C88A00;padding-top:16px}}
h2{{color:#0E4D2E}}blockquote{{border-left:3px solid #C88A00;margin:12px 0;padding:8px 16px;color:#64748b}}
nav{{position:sticky;top:0;background:#fff;padding:8px;border-bottom:1px solid #eee}}</style></head>
<body><div class="cover"><p>FAIR DINKUM PUBLISHING</p><h1>{cfg['title']}</h1>
<p>{cfg['subtitle']}</p><p>{cfg['prod']} · Flipbook Edition · 2026</p></div>
<hr>{'<hr>'.join(parts)}
<footer><p>© 2026 Fair Dinkum Publishing · ABN 63 590 716 023</p></footer></body></html>"""
    os.makedirs(cfg['out'], exist_ok=True)
    fp = os.path.join(cfg['out'], '01-flipbook.html')
    open(fp, 'w').write(doc)
    print(f"Flipbook {key}: pageless reflowable → {fp} ({os.path.getsize(fp)/1024:.0f} KB)")
    return fp

if __name__ == '__main__':
    which = (sys.argv[1] if len(sys.argv) > 1 else 'all').lower()
    keys = ['skate', 'graffiti'] if which == 'all' else [which]
    for k in keys:
        build_flipbook(k, BOOKS[k])
        build_pdf(k, BOOKS[k])
    print('Done.')
