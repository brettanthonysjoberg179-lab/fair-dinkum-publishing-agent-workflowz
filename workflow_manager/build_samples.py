#!/usr/bin/env python3
"""FDP free samples v2 — pro pagination engine (FDPDoc).
Usage: python3 build_samples.py [all|skate|graffiti|playbook|solo]
Cover (no folio) → content opens fresh (arabic p.1, running heads) → buy CTA.
"""
import os, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_ebook_pdf import (styles, md_to_flowables, FDPDoc, PRIMARY, ACCENT, GRAY)
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import (Paragraph, Spacer, PageBreak, HRFlowable,
                                ListFlowable, ListItem, NextPageTemplate)

SAMPLES = {
    'skate': dict(src='book/the-history-of-skateboarding', chs=1,
                  out='digital_product_workforce/outputs/prod-fairdinkum-ebook-003/build/03-sample.pdf',
                  title='The History of Skateboarding', prod='FDP-SKATE-003', price='$29 AUD'),
    'graffiti': dict(src='book/the-history-of-graffiti', chs=1,
                     out='digital_product_workforce/outputs/prod-fairdinkum-ebook-004/build/03-sample.pdf',
                     title='The History of Graffiti', prod='FDP-GRAF-004', price='$29 AUD'),
}

TEASERS = {
    'playbook': dict(out='digital_product_workforce/outputs/prod-fairdinkum-ebook-001/build/03-sample.pdf',
                     title='Aussie Agent Workflowz Playbook', prod='FDP-AAW-001', price='$49 AUD',
                     lines=['The Fair Dinkum Promise: 12 agent workflows, zero fluff.',
                            'The Core Framework: audit → tool-source → quality loop.',
                            'Step 1 Set Up Right: free + paid stack with AUD costs.',
                            'Money Talk: pricing in AUD, GST-inclusive thinking.',
                            'Get It Seen: Gumroad/Stripe/Square launch path.']),
    'solo': dict(out='digital_product_workforce/outputs/prod-fairdinkum-ebook-002/build/03-sample.pdf',
                 title='Solopreneur OS', prod='FDP-SOLO-002', price='$29 AUD',
                 lines=['From chaos to calm: one operating system for solo founders.',
                        'Capture: every task lands in one inbox.',
                        'Weekly review: 30 minutes that run the business.',
                        'Money day: pricing, pipeline, and pay-yourself-first.',
                        '30-day rollout plan inside the full book.']),
}

def _cover(story, st, cfg, label):
    story += [Spacer(1, 48), Paragraph(label, st['brand']),
              Paragraph(cfg['title'], st['cover_title']),
              Paragraph('First taste free — full book ' + cfg['price'], st['cover_sub']),
              Spacer(1, 12),
              HRFlowable(width='30%', color=ACCENT, thickness=2, hAlign='CENTER')]

def _cta(story, st, cfg):
    story += [NextPageTemplate('Body'), PageBreak(),
              Paragraph('Enjoyed the sample?', st['h1']),
              Paragraph(f"The full book ({cfg['prod']}) is {cfg['price']}, flipbook + PDF, GST-inclusive. "
                        f"Reply to any Fair Dinkum email for your checkout link.", st['body']),
              Paragraph('Fair Dinkum Publishing · Adelaide SA · ABN 63 590 716 023', st['caption'])]

def build_chapter_sample(key, cfg):
    st = styles()
    ch_files = sorted(glob.glob(os.path.join(cfg['src'], 'ch*.md')))[:cfg['chs']]
    assert ch_files
    from build_ebook_pdf import chapter_title_of
    titles = [chapter_title_of(c) for c in ch_files]
    story = []
    _cover(story, st, cfg, 'FREE SAMPLE')
    story += [NextPageTemplate('Chapter'), PageBreak(), NextPageTemplate('Body')]
    for ch in ch_files:
        story += md_to_flowables(ch, st)
    _cta(story, st, cfg)
    os.makedirs(os.path.dirname(cfg['out']), exist_ok=True)
    doc = FDPDoc(cfg['out'], cfg['title'] + ' — FREE SAMPLE', titles)
    doc.build(story)
    print(f"sample {key}: pro-paginated → {cfg['out']} ({os.path.getsize(cfg['out'])//1024} KB)")

def build_teaser_sample(key, cfg):
    st = styles()
    items = [ListItem(Paragraph(l, st['bullet']), leftIndent=18) for l in cfg['lines']]
    story = []
    _cover(story, st, cfg, 'FREE TEASER')
    story += [NextPageTemplate('Chapter'), PageBreak(), NextPageTemplate('Body'),
              Paragraph("What's inside the full book", st['h1']),
              ListFlowable(items, bulletType='bullet')]
    _cta(story, st, cfg)
    os.makedirs(os.path.dirname(cfg['out']), exist_ok=True)
    doc = FDPDoc(cfg['out'], cfg['title'] + ' — FREE TEASER', ["What's inside the full book"])
    doc.build(story)
    print(f"teaser {key}: pro-paginated → {cfg['out']} ({os.path.getsize(cfg['out'])//1024} KB)")

if __name__ == '__main__':
    which = (sys.argv[1] if len(sys.argv) > 1 else 'all').lower()
    for k in (['skate', 'graffiti'] if which == 'all' else ([which] if which in SAMPLES else [])):
        build_chapter_sample(k, SAMPLES[k])
    for k in (['playbook', 'solo'] if which == 'all' else ([which] if which in TEASERS else [])):
        build_teaser_sample(k, TEASERS[k])
    print('Done.')
