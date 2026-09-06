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

> ⚠️ **순서 함정 (2026-09-06 1차 수집 때 실제로 틀렸던 것)**
> 공홈 원본 파일명에는 `00_`, `01_` 같은 접두 번호가 있지만 일부는 `copy-1788425958-00_…`
> 처럼 앞에 복제 타임스탬프가 붙어 있다. **파일명을 정렬(sort)하면 순서가 뒤집힌다.**
> 마그네슘은 1차 수집 때 이 때문에 첫 장이 3번째로 밀렸다.
> 반드시 **HTML에 나타난 등장 순서**를 그대로 쓸 것 (`sort` 금지, 중복만 제거).
- 상품페이지(`site/product-*.html`) 의 상세 이미지 영역은 이 폴더를 소스로 쓴다.

## 다시 받는 방법 (원본이 갱신되면)

```
curl -A "Mozilla/5.0" "https://zengenetics.co.kr/product/detail.html?product_no=16&cate_no=1&display_group=1" -o p.html
grep -oE 'ec-data-src="/web/upload/NNEditor/[^"]+"' p.html | sed 's/ec-data-src="//;s/"$//' | awk '!seen[$0]++'
# 위 명령의 sort -u 는 쓰지 말 것 — awk '!seen[$0]++' 로 등장 순서를 유지하며 중복만 제거한다
# 각 경로 앞에 https://zengenetics.co.kr 를 붙여 --referer https://zengenetics.co.kr/ 로 받는다
```

상세 이미지는 `#prdDetailContentLazy` 안에서 **지연 로딩**되므로 `src` 가 아니라 `ec-data-src` 를 봐야 한다.
헤드리스 브라우저는 프록시가 막지만 **curl 은 통과한다.**
