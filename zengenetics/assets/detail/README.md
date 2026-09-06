# 상세페이지 원본 (공홈 실물)

2026-09-06, 공홈 zengenetics.co.kr 에서 직접 내려받은 **실제 판매 중인 상세페이지 전문**.
`reference/detail-jpg/` 의 90px 썸네일을 대체하는 **작업용 원본**이다.

| 폴더 | 제품 | 장수 | 출처 (cafe24 product_no) |
|---|---|---|---|
| `potassium/` | 젠제네틱스 포타슘 칼륨 (20ea) | 14 | 11 |
| `vitaminb/` | 젠제네틱스 비타민B컴플렉스 (20ea) | 15 | 13 |
| `magnesium/` | 젠제네틱스 마그네슘 (20ea) | 16 | 16 |

- 원본 폭 **1080px** PNG → WebP q88 변환 (제품당 약 1MB)
- 파일명은 공홈 게시 순서 그대로. `01.webp` 부터 순서대로 이어 붙이면 상세페이지 전문이 된다.
- 상품페이지(`site/product-*.html`) 의 상세 이미지 영역은 이 폴더를 소스로 쓴다.

## 다시 받는 방법 (원본이 갱신되면)

```
curl -A "Mozilla/5.0" "https://zengenetics.co.kr/product/detail.html?product_no=16&cate_no=1&display_group=1" -o p.html
grep -oE 'ec-data-src="/web/upload/NNEditor/[^"]+"' p.html | sed 's/ec-data-src="//;s/"$//' | sort -u
# 각 경로 앞에 https://zengenetics.co.kr 를 붙여 --referer https://zengenetics.co.kr/ 로 받는다
```

상세 이미지는 `#prdDetailContentLazy` 안에서 **지연 로딩**되므로 `src` 가 아니라 `ec-data-src` 를 봐야 한다.
헤드리스 브라우저는 프록시가 막지만 **curl 은 통과한다.**
