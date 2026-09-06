# SEO 고급설정 「코드 직접입력」 — PC 쇼핑몰 탭

대표님이 2026-09-06 관리자 화면에서 직접 복사해 주신 원문 기준. **이게 정본이다.**

| 파일 | 용도 |
|---|---|
| `PC_Head영역_수정전_백업.txt` | 손대기 전 원문 (되돌릴 때 이걸 붙여넣는다) |
| `PC_Head영역_수정본.txt` | **붙여넣을 것** — 위에서 3줄만 뺐다 |
| `PC_Body영역_변경없음.txt` | Body 는 고칠 게 없다. 대조용 |

## Head 에서 뺀 3줄 (1,386자 → 1,261자)

```html
<title>젠제네틱스｜건강한 파우더리 데일리 루틴</title>
<!-- Canonical 설정 -->
<link rel="canonical" href="https://zengenetics.co.kr/">
```

## 그대로 둔 것

`G-84HNK1MRBG` gtag · `GTM-5W5PV3CD` · `facebook-domain-verification` ·
`incentoSEOScriptV1.js` · description · keywords

## 교체 후 검증 결과 (Playwright, 라이브 소스에 실제 치환)

| | 수정 전 | 수정 후 |
|---|---|---|
| `<title>` | **2개**, 첫 번째(홈 문구)가 이김 | **1개** — `젠제네틱스 포타슘 칼륨 (20ea) \| …` |
| `canonical` | **2개 충돌** — 홈 + 상품 | **1개** — 상품 URL |
| og:title | 정상 | 정상(변화 없음) |
| 페이스북 인증 / incento / GTM / GA4 2종 | 있음 | **전부 유지** |

## 제가 처음에 틀렸던 것 (기록)

라이브 렌더 결과만 보고 필드 범위를 추정했더니 두 군데가 틀렸다.
- Head 끝의 `incentoSEOScriptV1.js` 를 **앱이 넣는 것으로 봤는데 필드 안에 있었다**
- Body 끝의 `<span itemscope>` 블록을 **필드 내용으로 봤는데 필드에 없었다**

→ 렌더 결과로 관리자 입력값을 역추정하면 경계를 틀린다. 원문을 받아야 한다.
