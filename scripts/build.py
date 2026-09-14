"""Build a dependency-free static weekly. Content is plain text, escaped as HTML."""
import json, re, shutil
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import urlsplit, quote

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist"
def e(value): return escape(str(value), quote=True)
def validate(issue):
    assert re.fullmatch(r"[a-z0-9-]+", issue['slug']), 'Invalid slug'
    date.fromisoformat(issue['date'])
    assert isinstance(issue['number'], int) and issue['number'] >= 0
    assert isinstance(issue['summary'], str) and issue['summary'].strip()
    assert issue['sections'], 'At least one section required'
    ids, urls = set(), set()
    for section in issue['sections']:
        assert re.fullmatch(r"[a-z0-9-]+", section['id']) and section['id'] not in ids
        ids.add(section['id'])
        assert section['title'].strip() and section['items']
        for item in section['items']:
            assert item['title'].strip() and item['paragraphs'] and item['links']
            assert all(isinstance(p, str) and p.strip() for p in item['paragraphs'])
            if not issue.get('demo'):
                assert item.get('source_name') and item.get('source_date'), 'Source attribution required'
                date.fromisoformat(item['source_date'])
                assert item['source_date'] <= issue['date'], 'Future source date'
            for link in item['links']:
                url = urlsplit(link['url'])
                assert url.scheme == 'https' and url.hostname and not url.username and not url.password
                assert link['label'].strip()
                urls.add(link['url'])
    return urls

def title(issue):
    return 'WP 台灣週報 · 示範刊' if issue.get('demo') else f"WP 台灣週報 · 第 {issue['number']} 期"

def page(heading, description, body, prefix='', right=''):
    icon = quote('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="#21667b"/><text x="16" y="23" text-anchor="middle" fill="#fffefa" font-family="serif" font-size="23">W</text></svg>')
    return f'''<!doctype html>
<html lang="zh-Hant-TW"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(heading)}</title><meta name="description" content="{e(description)}"><link rel="icon" type="image/svg+xml" href="data:image/svg+xml,{icon}"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;800&amp;family=Noto+Serif+TC:wght@600;700&amp;display=swap" rel="stylesheet"><link rel="stylesheet" href="{prefix}style.css"></head>
<body><a class="skip" href="#main">跳至主要內容</a><header class="site-header"><div class="wrap header-inner"><div><a class="brand" href="{prefix}index.html">《WP 台灣週報》</a><div class="tagline">獨立整理 · WordPress 台灣視角</div></div><nav class="header-links" aria-label="網站導覽">{right}</nav></div></header><main id="main" class="wrap site-main">{body}</main><footer class="wrap site-footer">WP 台灣週報 · 每週一整理 · 原文著作權屬各來源作者。本站非 WordPress 官方刊物。</footer></body></html>'''

def build():
    all_issues = [json.loads(p.read_text()) for p in sorted((ROOT/'content/issues').glob('*.json'))]
    seen_slug, seen_date, seen_number = set(), set(), set()
    registry = []
    for issue in all_issues:
        urls = validate(issue)
        assert issue['slug'] not in seen_slug, 'Duplicate slug'
        seen_slug.add(issue['slug'])
        if not issue.get('demo'):
            assert issue['date'] not in seen_date and issue['number'] not in seen_number, 'Duplicate issue'
            assert issue['number'] > 0 and date.fromisoformat(issue['date']).weekday() == 0, 'Use Monday publication date'
            seen_date.add(issue['date']); seen_number.add(issue['number'])
            registry.append({'date':issue['date'],'number':issue['number'],'slug':issue['slug'],'sources':sorted(urls)})
    real = [i for i in all_issues if not i.get('demo')]
    issues = sorted(real or all_issues, key=lambda i:(i['date'],i['number']), reverse=True)
    OUT.mkdir(exist_ok=True)
    shutil.rmtree(OUT/'issues', ignore_errors=True)
    (OUT/'issues').mkdir()
    cards = []
    for issue in issues:
        name = title(issue)
        label = '示範刊' if issue.get('demo') else f"第 {issue['number']} 期"
        number = '00' if issue.get('demo') else f"{issue['number']:02d}"
        cards.append(f'''<article class="panel archive-item"><div class="issue-badge" aria-hidden="true"><span class="issue-number">{number}</span><span class="issue-label">{'DEMO' if issue.get('demo') else 'ISSUE'}</span></div><div><div class="meta"><time datetime="{issue['date']}">{issue['date']}</time>　·　{label}</div><h2><a href="issues/{issue['slug']}.html" style="color:inherit">{e(name)}</a></h2><p class="excerpt">{e(issue['summary'])}</p><a class="read-link" href="issues/{issue['slug']}.html">閱讀本期 →</a></div></article>''')
        toc, sections = [], []
        for section in issue['sections']:
            toc.append(f'<li><a href="#{section["id"]}">{e(section["title"])}</a></li>')
            stories = []
            for item in section['items']:
                paragraphs = ''.join(f'<p>{e(p)}</p>' for p in item['paragraphs'])
                links = ''.join(f'<a class="pill" href="{e(l["url"])}" target="_blank" rel="noopener noreferrer">{e(l["label"])}</a>' for l in item['links'])
                meta = f'<p class="source-meta">來源：{e(item["source_name"])} · {e(item["source_date"])}</p>' if item.get('source_name') else ''
                stories.append(f'<article class="story"><h3>{e(item["title"])}</h3>{paragraphs}{meta}<div class="links">{links}</div></article>')
            sections.append(f'<section id="{section["id"]}" class="panel section"><h2>{e(section["title"])}</h2>{"".join(stories)}</section>')
        notice = '<p class="notice">版型示範：本頁為來源導覽，不是當週新聞，也不計入正式期數。</p>' if issue.get('demo') else ''
        hero = f'<div class="panel intro issue-hero"><div class="eyebrow">{"PREVIEW" if issue.get("demo") else "ISSUE " + str(issue["number"]).zfill(3)}</div><h1>{e(name)}</h1><p class="meta">{"示範日期" if issue.get("demo") else "出刊日"} <time>{issue["date"]}</time></p><p class="summary">{e(issue["summary"])}</p>{notice}</div>'
        body = hero + f'<div class="reading-layout"><aside class="panel toc"><nav aria-label="本期目錄"><h2>本期目錄</h2><ol>{"".join(toc)}</ol></nav></aside><div class="sections">{"".join(sections)}</div></div><div class="bottom-nav"><a href="../index.html">← 返回週報目錄</a></div>'
        right = f'<a class="pill" href="../index.html">目錄</a><span class="pill">{label} · {issue["date"]}</span>'
        (OUT/'issues'/f'{issue["slug"]}.html').write_text(page(name,issue['summary'],body,'../',right),encoding='utf-8')
    desc = '每週一手來源整理：Core、WooCommerce、台灣站務、社群與在地工作室。點任一期即可閱讀全文。'
    body = f'<section class="panel intro"><div class="eyebrow">ARCHIVE</div><h1>目錄</h1><p class="description">{desc}</p></section><div class="archive-list">{"".join(cards)}</div>'
    (OUT/'index.html').write_text(page('WP 台灣週報 · 目錄',desc,body,right=f'<span class="pill">目錄 · 共 {len(real)} 期</span>'),encoding='utf-8')
    (OUT/'.nojekyll').touch()
    (OUT/'published.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Built archive and {len(issues)} issue pages; {len(real)} published issues.')

if __name__ == '__main__': build()
