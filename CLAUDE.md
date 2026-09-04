# wespotjh 작업 저장소

`zengenetics/` = 젠제네틱스 홈페이지 리뉴얼 프로젝트 (cafe24 이식 전제). 작업 브랜치 `claude/ruflo-starter-setup-bctixb`.

## 세션 시작 시 반드시

1. `zengenetics/design-system.md` 읽기 — 모든 디자인 결정 로그 (단일 소스)
2. `zengenetics/team/README.md` 읽기 — 웹/모바일 개발팀 규정
3. **`zengenetics/reference/제품컨셉_바이블.md` 읽기 — 제품 3종 공식 컨셉·상세페이지 플로우 (2026-09-04 대표님 확정).** 원본 JPG 3장은 `zengenetics/reference/detail-jpg/` (절대 삭제 금지). 제품을 언급·묘사하는 모든 작업(카피·디자인·개발) 전에 필독이며, 각 역할 스폰 프롬프트에 요약표를 포함한다. 핵심: 칼륨=나트륨 배출→붓기제거 / 비타민B=**B1·B2·B6·B12 4종**·아침 활력 / 마그네슘=근육 회복·신경 회복(리커버리·숙면·밤)

## "개발팀 가동" 부팅 절차 (이 말이 나오면 즉시 수행)

대표님이 "개발팀", "웹팀", "팀 가동" 등을 말하면:
1. `zengenetics/team/` 차터 6종 읽기 (기획/디자인/개발/QA/컴플라이언스/팀장)
2. 현황판 DB에 출근 기록 — HQ 2층: https://claude.ai/code/artifact/a87031e9-8c97-4fa5-b16f-247c0e4e2de8
   (스키마는 team/README.md: `office/webrun`, `webagents/*`, `weblog`)
3. 파이프라인 순서대로 Agent 도구로 역할 스폰 (각 프롬프트 = 차터 전문 + 이전 산출물)
4. 단계마다 현황판 갱신, QA PASS + 심의 PASS + 팀장 승인 산출물만 대표님 보고

## "젠제네틱스 회사 나와" (호출어)

대표님이 "젠제네틱스 회사 나와", "회사 보여줘", "HQ" 등을 말하면 → 젠제네틱스 HQ 현황판 링크를 바로 제시한다: https://claude.ai/code/artifact/a87031e9-8c97-4fa5-b16f-247c0e4e2de8 (1F 광고팀 / 2F 웹·모바일 개발팀)

## 영구 규칙

- **메인 세션 단독 제작·단독 검수 금지** — 홈페이지 작업은 반드시 개발팀 파이프라인
- 대표님 확정 사항(design-system.md) 되돌리기 금지
- 컴플라이언스 가드레일: 칼륨(당류가공품) 기능성 표현 불가, 금지어 "루틴"·"웰니스", 얼굴 식별 스톡 금지, 지어낸 수치 금지
- 제품 비주얼은 실물 3D 렌더 아카이브(`zengenetics/assets/render/`)만 — AI로 제품을 새로 그리지 않는다
- 광고 소재 작업은 이 리포가 아니라 `wespotjh/zengenetics-meta-ads`(광고팀)에서
