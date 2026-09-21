#!/usr/bin/env python3
"""
regen_writeup_html.py: rebuild the styled .html twins of the writeups from their .md sources,
in English (0N-name.md to 0N-name.html) and Vietnamese (0N-name.vi.md to 0N-name.vi.html).

Run this AFTER tools/fill_portfolio.py, so the twins carry the injected measured tables.
index.html links to the .html twins, so they must exist and must match the markdown.

Stdlib only. It keeps each twin's existing <head>, styles, nav, and page script untouched and
replaces only the <article class="doc" id="doc"> body and the <title>. The page script rebuilds
its table of contents from the new headings.

Covers the markdown the writeups use: ATX headings, paragraphs, blockquotes, bold, italic,
inline code, links, tables, ordered and unordered lists, horizontal rules, fenced code blocks,
and raw HTML comment lines (the <!--measured:...--> markers pass through untouched).

Usage:  python3 tools/regen_writeup_html.py          (from anywhere; root inferred from this file)
"""
import io, re, html as H, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTICLE_OPEN = '<article class="doc" id="doc">'
WRITEUPS = [
    ('01-hieuluat-retrieval-optimization.html', 'Legal search path'),
    ('02-gen-system-inference-optimization.html', 'Local LLM inference'),
    ('03-reproducible-benchmarking.html', 'Benchmarking method'),
]

def slug(t):
    t = re.sub(r'<[^>]+>', '', t)
    t = re.sub(r'[^\w\s-]', '', t.lower())
    return re.sub(r'[\s_]+', '-', t).strip('-')

def inline(t):
    t = H.escape(t, quote=False)
    t = re.sub(r'`([^`]+)`', lambda m: '<code>' + m.group(1) + '</code>', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', t)
    return t

def convert(md):
    out, lines, i, para = [], md.split('\n'), 0, []
    def flush():
        if para:
            out.append('<p>' + inline(' '.join(x.strip() for x in para)) + '</p>')
            para.clear()
    while i < len(lines):
        ln = lines[i]; s = ln.strip()
        if s.startswith('```'):
            flush(); code = []; i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code.append(lines[i]); i += 1
            out.append('<pre><code>' + H.escape('\n'.join(code)) + '</code></pre>'); i += 1; continue
        if s.startswith('<!--'):
            flush(); out.append(s); i += 1; continue
        if not s:
            flush(); i += 1; continue
        if re.fullmatch(r'-{3,}', s):
            flush(); out.append('<hr>'); i += 1; continue
        m = re.match(r'^(#{1,6})\s+(.*)$', s)
        if m:
            flush(); lvl, txt = len(m.group(1)), m.group(2)
            out.append(f'<h{lvl} id="{slug(txt)}">{inline(txt)}</h{lvl}>'); i += 1; continue
        if s.startswith('>'):
            flush(); q = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                q.append(lines[i].strip()[1:].strip()); i += 1
            out.append('<blockquote>' + convert('\n'.join(q)) + '</blockquote>'); continue
        if s.startswith('|') and i + 1 < len(lines) and re.fullmatch(r'\|[\s|:-]*\|?', lines[i + 1].strip()):
            flush()
            hdr = [c.strip() for c in s.strip('|').split('|')]
            rows, i = [], i + 2
            while i < len(lines) and lines[i].strip().startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')]); i += 1
            t = ['<table>', '<thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in hdr) + '</tr></thead>', '<tbody>']
            for r in rows:
                t.append('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>')
            t += ['</tbody>', '</table>']; out.append('\n'.join(t)); continue
        m = re.match(r'^(\s*)([-*]|\d+\.)\s+(.*)$', ln)
        if m:
            flush(); ordered = m.group(2)[0].isdigit(); items = []
            while i < len(lines):
                mm = re.match(r'^(\s*)([-*]|\d+\.)\s+(.*)$', lines[i])
                if mm and (mm.group(2)[0].isdigit() == ordered):
                    items.append(mm.group(3)); i += 1
                    while i < len(lines) and lines[i].strip() and lines[i].startswith(' ') \
                            and not re.match(r'^\s*([-*]|\d+\.)\s+', lines[i]):
                        items[-1] += ' ' + lines[i].strip(); i += 1
                else:
                    break
            tag = 'ol' if ordered else 'ul'
            out.append(f'<{tag}>' + ''.join(f'<li>{inline(x)}</li>' for x in items) + f'</{tag}>'); continue
        para.append(ln); i += 1
    flush()
    return '\n'.join(out)

# ---------------------------------------------------------------- languages
# Each writeup has an English source (0N-name.md) and may have a Vietnamese one (0N-name.vi.md).
# Each source gets a styled twin next to it (.html and .vi.html). The Vietnamese twin is made from
# the English twin's shell the first time, then kept in sync the same way.
LANG = {
    'en': {
        'suffix': '', 'writeups': 'Portfolio writeups', 'portfolio': 'Portfolio',
        'labels': ['Legal search path', 'Local LLM inference', 'Benchmarking method'],
        'home': 'Home', 'bench': 'Benchmarks and evidence',
        'switch_label': 'Language', 'switch_text': 'Ti\u1ebfng Vi\u1ec7t',
    },
    'vi': {
        'suffix': '.vi', 'writeups': 'B\u00e0i vi\u1ebft', 'portfolio': 'Portfolio',
        'labels': ['\u0110\u01b0\u1eddng t\u00ecm ki\u1ebfm ph\u00e1p lu\u1eadt', 'Inference LLM c\u1ee5c b\u1ed9', 'Ph\u01b0\u01a1ng ph\u00e1p benchmark'],
        'home': 'Trang ch\u1ee7', 'bench': 'Benchmark v\u00e0 b\u1eb1ng ch\u1ee9ng',
        'switch_label': 'Ng\u00f4n ng\u1eef', 'switch_text': 'English',
    },
}

# page chrome of the Vietnamese twin: (english, vietnamese), applied only where the english is present
CHROME_VI = [
    ('<html lang="en"', '<html lang="vi"'),
    ('<span class="bt">Engineering<br>Writeups</span>', '<span class="bt">B\u00e0i vi\u1ebft<br>k\u1ef9 thu\u1eadt</span>'),
    ('Architecture and measured results: the web version of the portfolio writeups.', 'Ki\u1ebfn tr\u00fac v\u00e0 k\u1ebft qu\u1ea3 \u0111o: b\u1ea3n web c\u1ee7a c\u00e1c b\u00e0i vi\u1ebft trong portfolio.'),
    ('<span class="progress-label">Reading progress</span>', '<span class="progress-label">Ti\u1ebfn \u0111\u1ed9 \u0111\u1ecdc</span>'),
    ('<span>Read aloud<span', '<span>\u0110\u1ecdc to<span'),
    ('>Listen sentence by sentence<', '>Nghe t\u1eebng c\u00e2u<'),
    (">Your browser doesn't support speech synthesis.<", '>Tr\u00ecnh duy\u1ec7t n\u00e0y kh\u00f4ng h\u1ed7 tr\u1ee3 \u0111\u1ecdc to.<'),
    ('id="raStatus">Idle<', 'id="raStatus">\u0110ang ngh\u1ec9<'),
    ('<label for="raRate">Speed <span', '<label for="raRate">T\u1ed1c \u0111\u1ed9 <span'),
    ('<label for="raVoice">Voice</label>', '<label for="raVoice">Gi\u1ecdng \u0111\u1ecdc</label>'),
    ('Theme &amp; position save in this browser.', 'Giao di\u1ec7n v\u00e0 v\u1ecb tr\u00ed \u0111\u1ecdc \u0111\u01b0\u1ee3c l\u01b0u trong tr\u00ecnh duy\u1ec7t n\u00e0y.'),
    ('<button id="resetBtn">Reset reading position</button>', '<button id="resetBtn">\u0110\u1eb7t l\u1ea1i v\u1ecb tr\u00ed \u0111\u1ecdc</button>'),
    ('aria-label="Open contents"', 'aria-label="M\u1edf m\u1ee5c l\u1ee5c"'),
    ('aria-label="Toggle light/dark theme"', 'aria-label="Chuy\u1ec3n giao di\u1ec7n s\u00e1ng t\u1ed1i"'),
    ('aria-label="Previous sentence"', 'aria-label="C\u00e2u tr\u01b0\u1edbc"'),
    ('aria-label="Play / pause"', 'aria-label="Ph\u00e1t / t\u1ea1m d\u1eebng"'),
    ('aria-label="Next sentence"', 'aria-label="C\u00e2u sau"'),
    ('aria-label="Stop"', 'aria-label="D\u1eebng"'),
    ("auto.textContent='Automatic';", "auto.textContent='T\u1ef1 \u0111\u1ed9ng';"),
    ("statusEl.textContent = !playing ? 'Idle' :\n       (paused?'Paused':('Reading '+(idx+1)+' / '+sentences.length));",
     "statusEl.textContent = !playing ? '\u0110ang ngh\u1ec9' :\n       (paused?'T\u1ea1m d\u1eebng':('\u0110ang \u0111\u1ecdc '+(idx+1)+' / '+sentences.length));"),
    ("var en=voices.filter(function(v){return /^en(-|$)/i.test(v.lang);});", "var en=voices.filter(function(v){return /^vi(-|$)/i.test(v.lang);});"),
    ("var u=new SpeechSynthesisUtterance(sentences[idx].text);", "var u=new SpeechSynthesisUtterance(sentences[idx].text); u.lang='vi-VN';"),
]


def build_twin(md_path, html_path, lang, base, index):
    L = LANG[lang]
    md = io.open(md_path, encoding='utf-8').read()
    s = io.open(html_path, encoding='utf-8').read()
    a = s.find(ARTICLE_OPEN); b = s.find('</article>')
    if a < 0 or b < a:
        print(f'  !! {html_path.name}: article slot not found, left untouched'); return False
    a += len(ARTICLE_OPEN)
    body = convert(md)
    # inside the web version, stay in the web version: sibling writeups open as .html
    # (0N-name.vi.md becomes 0N-name.vi.html), and directory links become README links.
    body = re.sub(r'href="(0[0-9]-[^"]+)\.md"', r'href="\1.html"', body)
    body = re.sub(r'href="(\.\./projects/[a-z0-9-]+)/"', r'href="\1/README%s.md"' % L['suffix'], body)
    s = s[:a] + '\n' + body + '\n' + s[b:]
    m = re.search(r'^#\s+(.+)$', md, re.M)
    if m:
        title = H.escape(m.group(1), quote=False)
        s = re.sub(r'<title>.*?</title>', '<title>' + title + '</title>', s, count=1, flags=re.S)
        # the rail heading is the same title, so the three cannot drift
        s = re.sub(r'<h1 class="title">.*?</h1>', '<h1 class="title">' + title + '</h1>', s, count=1, flags=re.S)
    if lang == 'vi':
        for en_text, vi_text in CHROME_VI:
            s = s.replace(en_text, vi_text)
        s = re.sub(r'<div class="kicker">Writeup · (\d+) of (\d+)</div>', lambda m: '<div class="kicker">Bài viết · %s trên %s</div>' % (m.group(1), m.group(2)), s)
    # the rail nav: the three writeups, the portfolio, and the other language, rebuilt every time
    cur = html_path.name
    sfx = L['suffix']
    nav = ['    <div class="guide-switch">', '      <div class="gs-label">%s</div>' % L['writeups']]
    links = ''
    for i, ((fname, _), label) in enumerate(zip(WRITEUPS, L['labels']), 1):
        target = fname[:-len('.html')] + sfx + '.html'
        klass = ' class="current"' if target == cur else ''
        links += f'<a href="{target}"{klass}>{i} \u00b7 {label}</a>'
    nav.append('      ' + links)
    nav.append('      <div class="gs-label" style="margin-top:14px;">%s</div>' % L['portfolio'])
    nav.append('      <a href="../index.html">%s</a><a href="../benchmarks/README%s.md">%s</a>'
               '<a href="../projects/gen-system/README%s.md">gen-system</a><a href="../projects/hieuluat/README%s.md">HieuLuat</a>'
               % (L['home'], sfx, L['bench'], sfx, sfx))
    other = base + ('.html' if lang == 'vi' else '.vi.html')
    if (html_path.parent / (base + '.vi.md')).exists():
        nav.append('      <div class="gs-label" style="margin-top:14px;">%s</div>' % L['switch_label'])
        nav.append('      <a href="%s" hreflang="%s">%s</a>' % (other, 'en' if lang == 'vi' else 'vi', L['switch_text']))
    nav.append('    </div>\n\n')
    s = re.sub(r'    <div class="guide-switch">.*?(?=    <div class="rail-foot">)', '\n'.join(nav), s, count=1, flags=re.S)
    io.open(html_path, 'w', encoding='utf-8', newline='\n').write(s)
    print(f'  regenerated {html_path.name}')
    return True


def main():
    done = 0
    for index, (fname, _) in enumerate(WRITEUPS, 1):
        base = fname[:-len('.html')]
        en_md, en_html = ROOT / 'writeups' / (base + '.md'), ROOT / 'writeups' / fname
        vi_md, vi_html = ROOT / 'writeups' / (base + '.vi.md'), ROOT / 'writeups' / (base + '.vi.html')
        if not en_html.exists():
            print(f'  skip {en_md.name}: no .html twin to update')
            continue
        if en_md.exists() and build_twin(en_md, en_html, 'en', base, index):
            done += 1
        if vi_md.exists():
            if not vi_html.exists():
                io.open(vi_html, 'w', encoding='utf-8', newline='\n').write(io.open(en_html, encoding='utf-8').read())
            if build_twin(vi_md, vi_html, 'vi', base, index):
                done += 1
    print(f'{done} twin(s) regenerated')
    return 0

if __name__ == '__main__':
    sys.exit(main())
