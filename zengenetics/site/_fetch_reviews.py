#!/usr/bin/env python3
"""젠제네틱스 알파리뷰 리뷰 추출 — 공식몰(mall_id=wespotjo) 상품별 리뷰 본문 수집"""
import json, time, urllib.request, urllib.parse, sys

BASE = "https://review-widget.alphwidget.com/v2/api-widget"
MALL, SHOP, WIDGET = "wespotjo", "1", "7ee3b8bd"
HDRS = {"Referer": "https://zengenetics.co.kr/", "Origin": "https://zengenetics.co.kr",
        "Accept": "application/json", "User-Agent": "Mozilla/5.0"}

def get(path, **q):
    url = f"{BASE}{path}?" + urllib.parse.urlencode(
        {"mall_id": MALL, "shop_no": SHOP, "widget_code": WIDGET, **q})
    req = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode())

def total(product_no):
    return get("/meta", product_no=product_no, page=1, page_size=3)

def pull(product_no, pages, delay=0.35):
    out = []
    for p in range(1, pages + 1):
        try:
            rows = get("", product_no=product_no, page=p, page_size=3)
        except Exception as e:
            print(f"  page {p} 실패: {e}", file=sys.stderr); break
        if not rows: break
        for r in rows:
            out.append({"id": r.get("id"), "ratings": r.get("ratings"),
                        "content": (r.get("content") or "").strip(),
                        "option": r.get("product_option"),
                        "product": (r.get("product") or {}).get("product_name")})
        time.sleep(delay)
    return out

if __name__ == "__main__":
    pno   = sys.argv[1] if len(sys.argv) > 1 else "11"
    pages = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    m = total(pno)
    print(f"product_no={pno}  총 리뷰 {m['total_count']:,}건 / 총 {m['total_page']:,}페이지")
    rows = pull(pno, pages)
    json.dump(rows, open(f"reviews_{pno}.json", "w"), ensure_ascii=False, indent=1)
    uniq = {r["id"] for r in rows}
    print(f"수집 {len(rows)}건 (고유 {len(uniq)}건) → reviews_{pno}.json")
    chars = sum(len(r["content"]) for r in rows)
    print(f"본문 총 {chars:,}자 / 건당 평균 {chars//max(len(rows),1)}자")
