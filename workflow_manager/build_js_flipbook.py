#!/usr/bin/env python3
"""FDP interactive JS flipbook: paginated, keyboard/touch nav, TOC sidebar, print CSS.
Usage: python3 build_js_flipbook.py [playbook|all]
Self-contained single HTML (no CDN) → prod-*/build/04-js-flipbook.html
"""
import os, sys, glob, html

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_ebook_pdf import BOOKS

WORDS_PER_PAGE = 220

def md_blocks(path):
    """Split markdown file into (kind, text) blocks."""
    out = []
    with open(path) as f:
        lines = f.read().split('\n')
    buf = []
    def flush():
        if buf:
            out.append(('p', ' '.join(buf))); buf.clear()
    for ln in lines:
        s = ln.strip()
        if not s:
            flush(); continue
        if s.startswith('```'):
            flush(); continue
        if s.startswith('### '): flush(); out.append(('h3', s[4:])); continue
        if s.startswith('## '): flush(); out.append(('h2', s[3:])); continue
        if s.startswith('# '): flush(); out.append(('h1', s[2:])); continue
        if s.startswith('---') or s == '***': flush(); out.append(('hr', '')); continue
        if s.startswith('>'): flush(); out.append(('q', s.lstrip('> '))); continue
        if s.startswith(('- ', '* ')): flush(); out.append(('li', s[2:])); continue
        import re
        if re.match(r'^(\d+)[.)]\s+', s): flush(); out.append(('li', re.sub(r'^(\d+)[.)]\s+', '', s))); continue
        if s.startswith('|'): continue
        buf.append(s)
    flush()
    return out

def inline(t):
    import re
    t = html.escape(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', t)
    t = re.sub(r'`(.+?)`', r'<code>\1</code>', t)
    return t

def render(b):
    kind, t = b
    if kind == 'h1': return f"<h2 class='ch'>{inline(t)}</h2>"
    if kind == 'h2': return f"<h3>{inline(t)}</h3>"
    if kind == 'h3': return f"<h4>{inline(t)}</h4>"
    if kind == 'hr': return "<hr>"
    if kind == 'q': return f"<blockquote>{inline(t)}</blockquote>"
    if kind == 'li': return f"<li>{inline(t)}</li>"
    return f"<p>{inline(t)}</p>"

def paginate(blocks):
    pages, cur, words = [], [], 0
    for b in blocks:
        w = len(b[1].split())
        if b[0] == 'h1' and cur:
            pages.append(cur); cur, words = [], 0
        cur.append(b); words += w
        if words >= WORDS_PER_PAGE and b[0] in ('p', 'li'):
            pages.append(cur); cur, words = [], 0
    if cur: pages.append(cur)
    return pages

def build(key, cfg):
    ch_files = sorted(glob.glob(os.path.join(cfg['src'], 'ch*.md')))
    assert ch_files, f"no chapters in {cfg['src']}"
    all_pages, toc = [], []
    for ch in ch_files:
        blocks = md_blocks(ch)
        title = next((t for k, t in blocks if k == 'h1'), os.path.basename(ch))
        toc.append(title)
        for pg in paginate(blocks):
            all_pages.append((title, pg))
    total = len(all_pages)
    page_divs = []
    for i, (title, pg) in enumerate(all_pages):
        lis, htmls = [], []
        for b in pg:
            if b[0] == 'li': lis.append(b)
            else:
                if lis:
                    htmls.append('<ul>' + ''.join(f"<li>{inline(t)}</li>" for _, t in lis) + '</ul>'); lis = []
                htmls.append(render(b))
        if lis:
            htmls.append('<ul>' + ''.join(f"<li>{inline(t)}</li>" for _, t in lis) + '</ul>')
        page_divs.append(
            f"<section class='page' data-p='{i+1}' data-ch='{html.escape(title)}' hidden>"
            f"<div class='runhead'>{html.escape(title)}</div>{''.join(htmls)}"
            f"<div class='folio'>{i+1} / {total}</div></section>")
    toc_items = ''.join(f"<li><a href='#' data-go='{i+1}'>{html.escape(t)}</a></li>"
                        for i, t in enumerate(toc))
    doc = f"""<!DOCTYPE html><html lang="en-AU"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{cfg['title']} — Interactive Flipbook · Fair Dinkum Publishing</title>
<style>
:root{{--ink:#1e293b;--green:#0E4D2E;--gold:#C88A00}}
body{{font-family:Georgia,serif;color:var(--ink);margin:0;background:#f4f1ea}}
#app{{display:flex;min-height:100vh}}
#toc{{width:250px;background:#0E4D2E;color:#fff;padding:20px;flex-shrink:0}}
#toc h2{{color:#C88A00;font-size:15px}}#toc a{{color:#fff;text-decoration:none;font-size:14px}}
#toc li{{margin:6px 0;list-style:none}}#toc ul{{padding:0}}
#toc .buy{{display:block;background:#C88A00;color:#111!important;text-align:center;padding:10px;border-radius:6px;margin-top:16px;font-weight:bold}}
#main{{flex:1;display:flex;flex-direction:column;align-items:center;padding:24px}}
#book{{background:#fff;max-width:640px;width:100%;min-height:70vh;padding:48px 52px;box-shadow:0 4px 24px rgba(0,0,0,.15);border-radius:4px;line-height:1.7}}
.runhead{{font-size:12px;color:#888;border-bottom:1px solid #eee;padding-bottom:8px;margin-bottom:16px;font-family:Arial,sans-serif}}
.folio{{text-align:center;color:#888;font-size:13px;margin-top:24px;font-family:Arial,sans-serif}}
.ch{{color:var(--green);border-top:3px solid var(--gold);padding-top:16px}}
h3{{color:var(--green)}}blockquote{{border-left:3px solid var(--gold);margin:12px 0;padding:8px 16px;color:#555}}
#nav{{display:flex;gap:12px;margin:16px;align-items:center;font-family:Arial,sans-serif}}
#nav button{{background:var(--green);color:#fff;border:0;padding:10px 22px;border-radius:6px;font-size:16px;cursor:pointer}}
#nav button:disabled{{opacity:.35}}
#cover{{text-align:center;padding:40px 0}}.flip{{transition:opacity .18s}} .flip.out{{opacity:0}}
@media(max-width:800px){{#toc{{display:none}}#book{{padding:24px}}}}
@media print{{#toc,#nav{{display:none}}#book{{box-shadow:none}}.page{{display:block!important}}}}
</style></head>
<body><div id="app">
<nav id="toc"><h2>{cfg['title']}</h2><ul>{toc_items}</ul>
<a class="buy" href="#">Buy full book</a></nav>
<div id="main"><div id="book" class="flip">{''.join(page_divs)}</div>
<div id="nav"><button id="prev">← Prev</button><span id="pos"></span><button id="next">Next →</button></div>
<p style="font-size:12px;color:#888">© 2026 Fair Dinkum Publishing · ABN 63 590 716 023</p></div></div>
<script>
const pages=[...document.querySelectorAll('.page')];let cur=0;const book=document.getElementById('book');
function show(n){{cur=Math.max(0,Math.min(pages.length-1,n));
book.classList.add('out');
setTimeout(()=>{{pages.forEach((p,i)=>p.hidden=i!==cur);
document.getElementById('pos').textContent=(cur+1)+' / '+pages.length;
document.getElementById('prev').disabled=cur===0;
document.getElementById('next').disabled=cur===pages.length-1;
book.classList.remove('out');if(location.hash)history.replaceState(null,'',' ');
try{{localStorage.setItem('fdp-{key}-page',cur)}}catch(e){{}}}},140);}}
document.getElementById('prev').onclick=()=>show(cur-1);
document.getElementById('next').onclick=()=>show(cur+1);
document.addEventListener('keydown',e=>{{if(e.key==='ArrowRight')show(cur+1);if(e.key==='ArrowLeft')show(cur-1);}});
document.querySelectorAll('#toc a[data-go]').forEach(a=>a.onclick=e=>{{e.preventDefault();show(+a.dataset.go-1);}});
let tx=null;book.addEventListener('touchstart',e=>tx=e.touches[0].clientX,{{passive:true}});
book.addEventListener('touchend',e=>{{const dx=e.changedTouches[0].clientX-tx;if(dx<-50)show(cur+1);if(dx>50)show(cur-1);}},{{passive:true}});
try{{cur=+(localStorage.getItem('fdp-{key}-page')||0)}}catch(e){{}}
pages.forEach((p,i)=>p.hidden=i!==cur);
document.getElementById('pos').textContent=(cur+1)+' / '+pages.length;
show(cur);
</script></body></html>"""
    os.makedirs(cfg['out'], exist_ok=True)
    fp = os.path.join(cfg['out'], '04-js-flipbook.html')
    open(fp, 'w').write(doc)
    print(f"JS flipbook {key}: {total} pages → {fp} ({os.path.getsize(fp)//1024} KB)")
    return fp

if __name__ == '__main__':
    which = (sys.argv[1] if len(sys.argv) > 1 else 'playbook').lower()
    keys = ['playbook', 'skate', 'graffiti', 'solo'] if which == 'all' else [which]
    for k in keys:
        build(k, BOOKS[k])
    print('Done.')
