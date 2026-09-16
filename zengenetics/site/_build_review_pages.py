#!/usr/bin/env python3
"""
젠제네틱스 리뷰 — 서버렌더 정적 리뷰 페이지 생성기

입력 (둘 중 아무거나):
  * fetch_reviews.py 산출 JSON        : --json reviews_11.json
  * 알파리뷰 어드민 엑셀 내보내기 CSV : --csv alpha_export.csv

산출:
  out/reviews-<product>-p1.html ...   크롤러가 JS 없이 읽는 리뷰 본문 페이지
  out/심의검토_대상.csv                미인정 기능성 표현 포함 리뷰 (검수용)

설계 원칙 (건강기능식품 표시·광고 심의 대응):
  - 이용후기 원문을 작성일 역순으로 '전량' 싣는다. 골라 싣지 않는다 (= 광고 아님)
  - 브랜드가 쓴 효능 문장을 한 줄도 넣지 않는다
  - 페이지에 실제로 보이는 리뷰만 Review 구조화 데이터로 마크업한다
"""
import argparse, csv, html, json, os, re, sys
from datetime import datetime

PER_PAGE = 50

# 칼륨 인정 기능성 밖의 표현 → 검수 대상으로 분리 (삭제하지 않고 플래그만)
RISK = {
    "체중·다이어트": r"체중|몸무게|다이어트|감량|\d+\s*(kg|키로|킬로)|살\s*빠",
    "질병·치료":     r"치료|완치|질병|병원|약\s*대신|처방|부종\s*치료",
    "의학적 단정":   r"효과\s*보장|100%|무조건|반드시\s*낫",
}

def load_json(p):
    rows = json.load(open(p, encoding="utf-8"))
    return [{"id": r.get("id"), "rating": r.get("ratings"),
             "content": (r.get("content") or "").strip(),
             "date": r.get("date") or "", "product": r.get("product") or ""} for r in rows]

def load_csv(p):
    """알파리뷰 엑셀 내보내기 CSV. 컬럼명이 버전마다 달라 후보로 매칭."""
    def pick(row, *names):
        for n in names:
            for k in row:
                if k and n in k.replace(" ", ""):
                    return (row[k] or "").strip()
        return ""
    out = []
    with open(p, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            out.append({"id": pick(row, "리뷰번호", "리뷰ID", "id"),
                        "rating": pick(row, "평점", "별점", "rating"),
                        "content": pick(row, "리뷰내용", "내용", "본문", "content"),
                        "date": pick(row, "작성일", "등록일", "date"),
                        "product": pick(row, "상품명", "product")})
    return [r for r in out if r["content"]]

def screen(rows):
    flagged = []
    for r in rows:
        hits = [lab for lab, pat in RISK.items() if re.search(pat, r["content"])]
        if hits:
            flagged.append({**r, "사유": " / ".join(hits)})
    return flagged

def esc(s): return html.escape(s or "", quote=True)

def page_html(rows, product, page, total_pages, total_count, base):
    items, ld = [], []
    for r in rows:
        body = esc(r["content"]).replace("\n", "<br>")
        rating = r.get("rating") or ""
        items.append(
            f'<li class="rv" itemscope itemtype="https://schema.org/Review">'
            f'<div class="rv-h"><span class="rv-s">평점 '
            f'<span itemprop="reviewRating" itemscope itemtype="https://schema.org/Rating">'
            f'<span itemprop="ratingValue">{esc(str(rating))}</span></span></span>'
            f'<span class="rv-d">{esc(r.get("date",""))}</span></div>'
            f'<div class="rv-b" itemprop="reviewBody">{body}</div></li>')
        if rating:
            ld.append({"@type": "Review",
                       "reviewRating": {"@type": "Rating", "ratingValue": rating},
                       "reviewBody": r["content"][:1500]})
    nav = []
    if page > 1:            nav.append(f'<a rel="prev" href="{base}-p{page-1}.html">이전</a>')
    if page < total_pages:  nav.append(f'<a rel="next" href="{base}-p{page+1}.html">다음</a>')

    jsonld = json.dumps({"@context": "https://schema.org", "@type": "ItemList",
                         "name": f"{product} 구매 후기", "numberOfItems": len(ld),
                         "itemListElement": ld}, ensure_ascii=False)

    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(product)} 구매 후기 {page}/{total_pages}페이지</title>
<meta name="description" content="{esc(product)} 구매 고객이 직접 작성한 이용후기 {total_count:,}건 중 {page}페이지.">
<link rel="canonical" href="https://zengenetics.co.kr/{base}-p{page}.html">
<style>
body{{font:16px/1.7 -apple-system,"Apple SD Gothic Neo",sans-serif;margin:0;color:#15161A;background:#fff}}
.w{{max-width:760px;margin:0 auto;padding:24px 20px 64px}}
h1{{font-size:20px;margin:0 0 4px}} .sub{{color:#5F626C;font-size:14px;margin:0 0 24px}}
ul{{list-style:none;padding:0;margin:0}}
.rv{{border-top:1px solid #E9E8E4;padding:18px 0}}
.rv-h{{display:flex;justify-content:space-between;font-size:13px;color:#5F626C;margin-bottom:6px}}
.rv-b{{white-space:pre-wrap;word-break:break-word}}
.nav{{margin-top:32px;display:flex;gap:16px}} .nav a{{color:#1A2B6B}}
.note{{margin-top:40px;padding-top:16px;border-top:1px solid #E9E8E4;font-size:12.5px;color:#93959D}}
</style>
<script type="application/ld+json">{jsonld}</script>
</head><body><div class="w">
<h1>{esc(product)} 구매 후기</h1>
<p class="sub">총 {total_count:,}건 · {page}/{total_pages}페이지 · 구매 고객이 직접 작성한 이용후기입니다.</p>
<ul>{''.join(items)}</ul>
<div class="nav">{''.join(nav)}</div>
<p class="note">본 페이지는 구매 고객이 작성한 이용후기를 작성일 역순으로 그대로 게시한 것이며,
판매자가 선별하거나 편집하지 않았습니다. 개인의 후기는 섭취에 따른 효과를 보증하지 않습니다.
건강기능식품은 질병의 예방·치료를 위한 의약품이 아닙니다.</p>
</div></body></html>"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json"); ap.add_argument("--csv")
    ap.add_argument("--product", default="젠제네틱스 포타슘 칼륨 (20ea)")
    ap.add_argument("--slug", default="reviews-potassium")
    ap.add_argument("--total", type=int, default=0, help="실제 총 리뷰수(표기용). 0이면 수집분 기준")
    ap.add_argument("--out", default="out")
    a = ap.parse_args()
    if not (a.json or a.csv): sys.exit("--json 또는 --csv 필요")

    rows = load_json(a.json) if a.json else load_csv(a.csv)
    rows = [r for r in rows if r["content"]]
    total_count = a.total or len(rows)
    os.makedirs(a.out, exist_ok=True)

    pages = [rows[i:i+PER_PAGE] for i in range(0, len(rows), PER_PAGE)] or [[]]
    for i, chunk in enumerate(pages, 1):
        fp = os.path.join(a.out, f"{a.slug}-p{i}.html")
        open(fp, "w", encoding="utf-8").write(
            page_html(chunk, a.product, i, len(pages), total_count, a.slug))

    flagged = screen(rows)
    if flagged:
        fp = os.path.join(a.out, "심의검토_대상.csv")
        with open(fp, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["id", "rating", "date", "사유", "content"],
                               extrasaction="ignore")
            w.writeheader(); w.writerows(flagged)

    chars = sum(len(r["content"]) for r in rows)
    print(f"리뷰 {len(rows):,}건 → {len(pages)}페이지 생성 ({a.out}/{a.slug}-p*.html)")
    print(f"크롤러가 읽을 본문: {chars:,}자 (현재 상세페이지는 130자)")
    print(f"심의 검토 대상: {len(flagged)}건" + (f" → {a.out}/심의검토_대상.csv" if flagged else ""))

if __name__ == "__main__":
    main()
