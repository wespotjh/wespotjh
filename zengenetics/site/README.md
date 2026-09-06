# zengenetics/site — 진짜 결과물 (단일 진실원장)

> **이 폴더가 현재 살아 있는 젠제네틱스 리뉴얼 페이지 전부다.**
> `zengenetics/prototype/` 은 **폐기된 옛 계보**다. 절대 그쪽을 최신본으로 보고하지 말 것.

## 왜 이 폴더가 생겼나 (2026-09-06)

이전 세션(개발팀장 나윤설)이 만든 커밋 24개가 **저장소에 푸시되지 못한 채 세션 안에만 갇혀 있었다.**
`wespotjh/wespotjh` 가 그 세션의 허용 목록에 없었기 때문이다. 그 결과:

- 진짜 결과물은 **아티팩트에만** 살아 있었고,
- 저장소에는 09-04에서 멈춘 옛 `prototype/home.html` 만 남아 있었고,
- 새 세션이 그 옛 파일을 "최신"으로 대표님께 보고하는 사고가 났다.

이 폴더는 그 사고를 끝내기 위해 **살아 있는 아티팩트 3종을 그대로 저장소에 박아 넣은 것**이다.

## 파일 ↔ 아티팩트 대응

| 파일 | 페이지 | 아티팩트 (라이브) |
|---|---|---|
| `home.html` | 홈 (전체 연결본) | https://claude.ai/code/artifact/9656f1c2-3dd7-4f5f-b9a8-a26d74b25be8 |
| `product-potassium.html` | 칼륨 상품페이지 | https://claude.ai/code/artifact/9ee9223d-6eff-4d2d-8d97-9e50927adbe1 |
| `product-vitaminb.html` | 비타민B컴플렉스 상품페이지 | https://claude.ai/code/artifact/a95de7da-56b0-43b6-bd19-ac997e830b4a |
| `product-magnesium.html` | 마그네슘 상품페이지 | https://claude.ai/code/artifact/4cd6d9e9-53fc-45ad-b8fb-6170e3d4e090 |
| `index.html` | **전체 페이지 목록 (대표님 열람용 랜딩)** | https://claude.ai/code/artifact/f0344bc4-53c7-4a2e-9fed-fe880c721d98 |
| `style-guide.html` | **브랜드·디자인 스타일 가이드 (외부 협업자 전달용, 전체 복사 버튼)** | https://claude.ai/code/artifact/c33ab57e-0536-47ed-9cf5-cfd3902f617e |
| `product-set-kmb.html` | 칼마비 세트 상품페이지 | https://claude.ai/code/artifact/abe7bfbd-cce3-478c-97d4-526284dd94e0 |
| `product-first-buy.html` | **생애 첫 구매 EVENT** (옵션 4종) | https://claude.ai/code/artifact/03ca55f6-b81f-43b3-afec-95695869e1bf |
| `product-daypack-potassium.html` | **칼륨 데이팩** (6포) | https://claude.ai/code/artifact/a4157239-8087-48d0-9423-ec0d287f8c20 |
| `product-daypack-magnesium.html` | **마그네슘 데이팩** (6포) | https://claude.ai/code/artifact/4de04db4-4a97-4caa-8904-e52e6527f1da |
| `product-daypack-vitaminb.html` | **비타민B 데이팩** (6포) | https://claude.ai/code/artifact/16a37a90-f6aa-41c3-83bb-9be2e06f97a0 |
| `product-set-swell.html` | **붓기 부스터** 세트 상품페이지 | https://claude.ai/code/artifact/3fa36b43-5e8d-46a3-bc9d-57f0aa009c60 |
| `product-set-performance.html` | **퍼포먼스 부스터** 세트 상품페이지 | https://claude.ai/code/artifact/02650a10-0f76-423b-9141-62ee3fd3b3be |
| `brand-story.html` | 브랜드 스토리 「하루를 고르게」 (구 「적을 수 있는 것만」) | https://claude.ai/code/artifact/1fd7a5ca-973c-4731-b9db-af263ab98343 |

각 파일은 아티팩트 서비스가 감싸는 `<!doctype html>…<head>` 래퍼를 포함한 **라이브 전문 그대로**다.

## 작업 규칙 (영구)

1. 페이지를 고치면 **이 폴더의 파일을 고치고 → 같은 아티팩트 URL로 republish → 즉시 커밋·푸시**한다. 셋 중 하나라도 빠지면 다시 잃어버린다.
2. republish 는 반드시 `url` 파라미터로 위 URL을 지정한다. 안 그러면 새 아티팩트가 생겨 대표님 북마크가 끊긴다.
3. 새 대화에서 첫 publish 전에는 `action:"read"` 로 먼저 읽는다.
4. `prototype/` 은 참고용 화석이다. 거기서 파생 작업하지 않는다.

## 폐기된 것

- `zengenetics/prototype/home.html` — 09-04 커밋 `30de191` 에서 멈춘 옛 계보. 아티팩트 `247e23e7-…` 가 이 파일을 가리킨다.
- 2026-09-06 오전 이 옛 파일 위에 진행된 히어로 재작업(홍시아 설계 → 이도현 구현)도 같은 이유로 폐기. 설계·구현 보고서는 `team/보고/` 에 근거로만 남긴다.
- ⚠️ 그 히어로 재작업분은 커밋 `24f9f43` 에 **QA FAIL 상태 그대로** 들어가 있다 (신아린 판정: 데스크톱 CTA 미노출 등 7건). `prototype/` 은 어차피 폐기이므로 고치지 않는다. **이 파일을 되살려 쓰지 말 것.**

## 세트 페이지 빌더

세트 3종 + 데이팩 3종 + 첫구매 EVENT, 총 **7장이 한 소스에서 생성**된다.
- 템플릿 `_set.tpl` · 빌더 `_build_set.py` (설정 CFG 안에 3종 값이 다 있다)
- 상세 이미지는 `assets/detail/set-{kmb,swell,performance}/` (공홈 게시 순서 그대로, `_source_urls.txt` 동봉)
- 문구·가격을 고칠 땐 **빌더의 CFG를 고치고 다시 돌린다.** HTML을 직접 손대면 다음 빌드에 덮인다.
- 돌린 뒤 반드시 **같은 아티팩트 URL로 republish → 커밋·푸시**.

### 빌더가 지원하는 것 (2026-09-06 확장)

- `was=None` → **정가 줄과 할인율을 아예 넣지 않는다.** 정가=판매가인 데이팩(60번)처럼
  cafe24가 정가 줄을 자동으로 숨기는 경우와 화면을 맞추기 위한 것.
- `options=[…]` → 카페24 옵션 선택 블록을 그린다 (첫구매 EVENT의 1+1 4종).
  옵션이 있으면 **상품금액·할인금액 줄을 숨긴다** — 옵션마다 정가 기준이 달라
  지어낸 할인액을 보여주지 않기 위해서다. 실제 값은 cafe24 주문서가 계산한다.
- `maxqty` → 수량 상한. 첫구매 EVENT는 계정당 1개라 `maxqty=1`.
