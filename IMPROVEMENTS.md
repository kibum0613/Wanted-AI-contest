# AI Home Layout Debugger — 개선 결과

작업 브랜치: `improvements`

작업일: 2026-09-20

원칙: **모든 좌표·측정값·위반·점수·해결 가능 여부는 결정론적 엔진이 계산한다. AI는 요청을 구조화하고 검증된 사실을 설명한다.**

## 공개 배포 사전 준비

승인부터 서버 배포·재배포·비용 관리까지의 전체 기록은 [DEPLOYMENT.md](DEPLOYMENT.md)를 따른다.

클라우드 자원/공개 URL과 별도로 애플리케이션 배포 전제 조건을 구현했다.
**배포 상태: 공개 기동/UI/결정론적 기능, 실제 AI 설명·영어 채팅·한국어/영어 삭제 명령을 검증했다. 최종 배포 코드 `3454627`.**
공개 앱: **<https://wanted-layout-kibum0613.azurewebsites.net>**.
실제 HTTPS에서 기본 9건·0점 → 자동 수정 5단계·0건·100점(최종 4.289초, 네트워크 포함),
저장·초기화·복원·Undo/Redo와 브라우저 3D 표시를 확인했다.
AI 분석·명령의 스키마 기반 JSON 출력과 잘린 응답의 적용 차단을 추가했고,
격리된 Linux Node를 사용한 전체 pytest **153개가 통과**했다(기존 경고 2개, 13.11초).
Windows `.exe` interop 실패 대응은 테스트 도구 환경에 한정했고 프로젝트 의존성은 추가하지 않았다.
후속 `347529a` 배포에서 설명 3.23초·`llm=true`·정상 구조 및 영어 채팅/정확한 ID 삭제가 성공했다.
이전 한국어 CLI 요청은 PowerShell 5의 `us-ascii` 파이프에서 HTTP 전에 물음표로 바뀌었다.
따라서 모델의 한국어 이해 부족이라는 결론은 철회한다. `_brief`의 실제 이름/ID 추가는 명확성·사용자 지정 이름 지원에 유효한 별도 개선이다.
관련 테스트 114개 및 최종 전체 **159개가 통과**했다(기존 경고 2개, **13.57초**, skip 없음).
`3454627` 배포도 성공했다(78초). Unicode를 보존한 “소파를 삭제해 줘”는 `delete/id=sofa` 작업,
“요청하신 소파를 삭제했습니다.” 응답 및 실제 씬의 소파 부재까지 확인했다(명령+후속 조회 3.221초).
공개 브라우저에서도 한국어 선택·실제 Unicode 입력·실행 후 소파 사이드바 항목이 사라지고 WebGL canvas가 유지됐다.
Demo Reset 클릭 후 소파와 기본 배치가 복귀하여 UI end-to-end 흐름까지 확인했다.
별도 진단에서 같은 설명 요청이 `STOP`과 정상 필드로 응답한 사실은 확인했으며 출력 예산은 4,096 tokens를 유지했다.
새 스키마 위반 응답을 임의로 복구하거나 빈 작업을 성공으로 처리하지 않고 명시적으로 거부한다.
Korea Central 학생 정책 거부 후 승인받은 Japan East Linux Basic B1 인스턴스 1개를 사용한다.
안내 비용은 **USD $0.019/시간·30일 $13.68**, 학생 크레딧 만료일은 **2027-08-18**이다.
spending limit On을 유지하고 유료 구독으로 업그레이드하지 않았다. 무료 Gemini 입력/응답의 제품 개선·사람 검토 가능성을 UI에 안내한다.
`rg-wanted-layout-demo`(그룹 메타데이터 Korea Central), `asp-wanted-layout-b1`(실제 플랜 Japan East),
`wanted-layout-kibum0613.azurewebsites.net`(Python 3.12/Always On/HTTPS/TLS 1.2/FTP 비활성화)이 준비되었다.
키는 사용자가 Azure 포털에 직접 등록했으며 애플리케이션 사전 테스트는 실제 키를 사용하지 않았다.
별도 일반 `Reply OK` 제공자 연결 시험과 실제 앱의 설명·채팅·명령 검증을 구분하여 기록했다.
Python App Service 코드 실행 경로는 임시 위치일 수 있으므로 영속 파일은 코드와 분리한 `/home/layout-data/`에 둔다.
`APP_ENV=production`, `LLM_PROVIDER=gemini-free`, `GEMINI_FREE_TIER_ONLY=true`,
`GEMINI_MODEL=gemini-3.5-flash-lite`, 무료 프로젝트의 `GEMINI_API_KEY`,
`AI_QUOTA_FILE=/home/layout-data/ai-quota.json`, `SAVED_LAYOUT_PATH=/home/layout-data/saved_layout.json`을 사용한다.
최종 시작 명령은 `sh /home/site/wwwroot/start_azure.sh`이며, 내부에서 uvicorn worker 1개·접근 로그 비활성화로 실행한다.
Azure `/home` 저장소 활성화 및 인스턴스 1개가 전제이며 `/api/health`가 설정과 저장소를 확인한다.
Oryx SDK 추출과 대량 파일 복사 정체를 조사한 뒤 전용 패키징 스크립트의 단일 압축 runtime ZIP으로 배포했다.
`SCM_DO_BUILD_DURING_DEPLOYMENT=false`, `ENABLE_ORYX_BUILD=false`를 **둘 다** 명시하고,
고정 `PYTHONPATH` 앱 설정은 제거해 시작 스크립트가 로컬 runtime 경로를 지정하도록 했다.
현대식 `az webapp deploy`가 **RuntimeSuccessful, 성공 1개/실패 0개**로 완료됐다.
OOM 원인은 확인되지 않았으므로 단정하지 않는다. 실제 재배포·재시작 후 저장/사용량 파일 해시가 동일하고 100점 저장본이 자동 로드됐다.
실제 동시 채팅은 하나 200/하나 429(`ai_busy`, Retry-After 5), 501자 질문은 제공자 호출 없이 422였다.

| 배포 전제 | 구현 / 확인 |
|---|---|
| 무료 전용 | 지정 모델만 HTTP 호출, 유료/다른 제공자·템플릿 자동 대체 없음; 결제 미연결 프로젝트는 운영자가 확인 |
| 공용 예산 | 10회/60초·400회/이동 24시간·동시 1회; 실패·명령 재시도도 개별 차감 |
| 재시작 안전성 | lock 파일 + 원자적 파일 교체 + fsync, 호출 전 예약; 저장소 손상·실패는 503, 초기화로 우회하지 않음 |
| 제한된 공개 입력 | 본문 128 KiB, 입력 500자, 대화 8×300자, 프롬프트/출력/씬 상한; Pydantic 공개 AI 요청 검증 |
| 오류 가시성 | 429/413/422/502/503/504 및 오류 코드·재시도 시간; AI 분석/명령/챗봇의 한국어·영어 표시 |
| 개인정보 고지 | 공용 씬, 민감정보 금지, 무료 Gemini의 제품 개선/사람 검토 가능성을 UI와 README에 표시 |
| 로컬 호환성 | `APP_ENV=local`, `LLM_PROVIDER=legacy`로 기존 키 우선순위/CLI/템플릿 동작 유지 |

추가 테스트는 네트워크를 가짜 전송기로 대체하여 실제 제공자 키나 할당량을 사용하지 않는다.
별도 Python 프로세스에서 사용량을 다시 읽는 재시작 검증, 동시 호출 차단, 재시도 한도 차단 시 부분 변경 없음,
제공자 오류의 HTTP/UI 전달과 이전 테스트를 함께 확인한다. 실제 클라우드 검증은 [DEPLOYMENT.md](DEPLOYMENT.md)에 별도로 구분했다.
최초 사전 준비 시 기존 80개를 포함하여 pytest **142개**, 구조화 출력 수정본 전체 **153개**, 최종 이름 문맥 개선본 전체 **159개**를 확인했다.
기본 9건→자동 수정 0건·100점은 기존 결정론적 엔진을 유지한다. 상세 운영 설정/한계는 README의 공개 배포 절을 따른다.

## 1. 단계별 변경

| 단계 | 구현 내용 | 확인한 동작 |
|---|---|---|
| 0. 테스트 기준선 | pytest, 테스트 격리, 코드·대상 쌍·측정값 고정 | 초기 6건·34점, 각 1순위 해결안의 재검증, 자동 수정 0건 |
| 1. 한국어/영어 | 전체 UI 언어 선택, 브라우저 선택 보관, API `lang`, 한글 가구 이름, 짧은 3D 라벨, 조사 헬퍼 | 언어 변경 시 좌표·점수·판정 불변, AI 출력 escape, 이전 언어의 늦은 응답 무시 |
| 2. 원본 보존 | `saved_layout.json` 원자적 저장, 시작 시 저장본 로드, 저장본 복원/데모 초기화 분리 | 원본 불변, 저장본 보존, 두 동작 Undo/Redo, 저장 오류·손상 파일 명시 |
| 3. 부족량 점수 | 위반별 `shortfall_mm`, `penalty`, 제한 감점 | 카드·검토 리포트와 엔진 점수 일치 |
| 4. 방향별 사용 공간 | 타입 기본값, 4방향 회전, 가구·벽·건물 외곽 검사, 침대 한 측면 규칙 | 책상–책장 400mm 유지, 초록/빨강 바닥 사각형 |
| 5. 동선 계산 | NumPy 100mm 격자, 600mm 폭 BFS, 가구 제거로 원인 추론, 경로 선 | 방문·가구 접근 검사, 옛 데이터 role 추론, 자동 수정 5초 이내 |
| 6. AI 적용 전 검증 | 복사본 일괄 검증, 1회 재시도, 동일 결과 확인 적용, 결정론적 `place` | 새 위반 시 미적용, AI 재호출 없는 확인, 토큰 만료, 부분 적용 방지 |
| 7. 해결안 확장 | 고정 구조 이동 금지, 대각선·회전+이동, 빠른 기하 필터 | 모든 후보 전체 재검증, 새 위반 유발 후보 제거 |
| 8. 정리·문서 | `Furniture`/`Walkway`, 옛 이름·JSON 키 호환, 깊이 0 접촉 수정 | 옛 씬 3종 로드, API 스키마 호환, 실행/규칙/API 문서 |

추가 검증 중 냉장고·세탁기의 사용 공간 설명이 범용 태그 때문에 책상 규칙을 먼저 가져올 수 있음을 발견했다.
위반 대상의 실제 타입을 함께 전달하고 해당 타입의 규칙을 우선 검색하도록 수정했다.

### 추가 요청: Wanted 스타일 디자인

제공된 Figma 자료는 로컬에서 확인하고, 밝은 배경·파란 강조색·둥근 컴포넌트·읽기 쉬운 글자와 여백을
자체 CSS로 반영했다. 기존 어두운 화면에서 헤더, 양쪽 패널, 버튼/입력, 검사 카드, 채팅, 리포트를 함께 정리했다.
3D 배경·그리드·라벨 색도 밝은 UI와 맞췄으며, 가구 형상이나 판정 로직은 바꾸지 않았다.
키보드 포커스·비활성 상태를 구분하고 375~1440px의 7개 화면 폭에서 가로 넘침과 제어 누락을 확인했다.
원본 Figma나 그 안의 이미지·폰트 자산을 외부에 업로드하거나 저장소에 복사하지 않았다.
마지막 실제 화면 검증에서 시작 시 저장본 존재 확인이 빠진 문제도 수정했다.
복원 버튼은 확인 전·저장본 없음·조회 실패 때 비활성화되며, 언어 전환·저장 후 상태 복구까지 회귀 검사한다.

## 2. 중요한 설계 결정

### 언어와 이름

- 기본값은 한국어이며 English로 전체 UI·검사 설명·해결안·AI 응답을 전환한다.
- `?lang=ko|en`은 표시만 변경한다. JSON ID와 가구의 저장 이름은 바꾸지 않는다.
- `소파 (거실)`의 3D 라벨은 `소파`이며 조사는 괄호 앞 단어 기준으로 판단한다.
- 받침이 있으면 `을/이/과`, 없으면 `를/가/와`를 쓴다.
- 방향은 `아래쪽(-Y)`처럼 평면도 기준으로 표시한다.
- 사용자 지정 이름과 이전 대화·수정 이력은 임의 번역하지 않는다.
- AI 문자열은 HTML로 실행되지 않도록 escape 또는 `textContent`로 표시한다.

### 저장

원본 [house2.json](backend/data/house2.json)을 덮어쓰지 않는다.
저장본은 `backend/data/saved_layout.json`에 별도로 기록하고 Git에서 제외한다.
같은 디렉터리의 임시 파일에 쓴 뒤 원자적으로 교체하므로 실패 시 기존 저장본이 유지된다.
**저장본 복원**은 저장본이 없으면 비활성화되며, **데모 초기화**는 저장본을 삭제하지 않는다.

### 점수

```text
shortfall_mm = max(required_mm - measured_mm, 0)
HIGH penalty = 10 + min(10, shortfall_mm / 50)
MEDIUM penalty = 4 + min(6, shortfall_mm / 50)
score = max(0, 100 - sum(penalty))
```

감점은 소수 첫째 자리로 반올림한다. 기본 감점은 심각도를 유지하고, 50mm당 1점의 추가 감점은
침범/부족 깊이를 반영한다. HIGH 20점, MEDIUM 10점으로 제한하여 한 위반이 점수를 무제한 지배하지 않게 했다.

### 앞면과 접근 면

| 타입 | 기준 |
|---|---|
| 책상 | 앞 750mm |
| 옷장·냉장고·세탁기 | 앞 600mm |
| 침대 | 긴 두 측면 중 하나라도 300mm 이상 |

회전은 Z축 반시계 방향으로 `0° → -Y`, `90° → +X`, `180° → +Y`, `270° → -X`이다.
기본 데모의 책상만 180°로 바꿔 남쪽 벽에서 방 안을 바라보게 했다. 다른 가구는 0°를 유지한다.
`maintenance_clearance_mm`은 타입 기본값을 덮어쓰며 0이면 해당 검사를 끈다.
구역과 바닥은 장애물이 아니고, 가구 너비 구간에 걸치는 가구·벽·건물 외곽만 측정한다.

### 동선과 성능

- 셀 중심 기준 가구·벽·외곽에서 300mm 미만인 셀을 막는다.
- 현관의 유효 셀을 시작점으로 4방향 BFS를 한 번 수행한다.
- 방문 구역과 사용 공간 가구 앞이 목표이며 침대는 어느 긴 측면이든 허용한다.
- 사람 중심이 설 수 있도록 목표 띠의 깊이는 최소 600mm로 잡는다.
- 막힌 목표는 가구를 하나씩 제외해 도달 가능해지는 대상을 원인으로 지정한다.
- 단일 가구 제거로 해결되지 않으면 고정 구조/여러 장애물로 명시한다.
- 원인 검사에서는 이미 도달한 영역을 재사용하고, 후보 검사에서는 표시용 경로 좌표 생성만 생략한다.
- 현관이 없는 옛 씬은 동선 검사 비활성화 사유를 API로 반환한다.

### AI 명령과 해결안

AI가 계산한 배치 가능성을 신뢰하지 않는다. 작업 목록을 복사본에 일괄 적용하고 전체 검사한다.
새 위반이면 원본을 유지한 채 한 번만 피드백 재시도한다. 실패한 제안의 **그래도 적용**은 서버에 보관된
동일 결과만 적용한다. 다른 편집·Undo/Redo 후에는 토큰이 만료된다.

`place`는 방·가구 타입 또는 ID·가까이 둘 대상만 받는다. 엔진이 100mm × 4방향 후보를 만들고
빠른 기하 필터를 적용한 뒤 거리순 상위 최대 64개를 전체 검사한다.
해결안은 축 이동/회전부터 시작하고 깨끗한 후보가 2개 미만이면 대각선/회전+이동까지 확장한다.
고정 구조는 이동하지 않으며 새 위반을 만드는 후보는 표시하거나 자동 적용하지 않는다.

## 3. 기본 데모 검사 결과

원래 6건은 그대로 유지하며 사용 공간 코드만 `MAINTENANCE_SPACE`에서 `USAGE_SPACE`로 바꿨다.
옷장이 침실 입구를 막는 기존 배치를 동선 엔진으로 검사하면서 접근 실패 3건이 추가됐다.
위반을 숨기기 위해 원본 가구를 재배치하지 않았다.

| 코드 | 대상 a | 대상 b | 부족량 mm | 감점 |
|---|---|---|---:|---:|
| HARD_CLASH | sofa | table | 250 | 15 |
| HARD_CLASH | tv_stand | wall_b | 150 | 13 |
| ZONE_INTRUSION | bed | bedroom_window | 400 | 10 |
| ZONE_INTRUSION | wardrobe | bedroom_door_swing | 300 | 10 |
| USAGE_SPACE | desk | bookshelf | 350 | 10 |
| OUT_OF_ROOM | tv_stand | living | 300 | 16 |
| CIRCULATION | bedroom_door_swing | wardrobe | 600 | 20 |
| CIRCULATION | bed | wardrobe | 600 | 20 |
| CIRCULATION | wardrobe | wardrobe | 600 | 20 |

마지막 행은 옷장 자신의 위치가 그 앞 접근도 막는다는 의미이다.
동선 실패의 600mm는 연속적인 실제 틈새 측정값이 아니라 `도달 불가=측정 0 / 요구 600`의 규칙 표현이다.

- 검사 **156개**, 위반 **9건**: HIGH 6 / MEDIUM 3.
- 감점 합계 134점, 최저점 제한 적용 후 **0점**.
- 자동 수정 **5회**, 모두 새 위반 없는 검증된 수정.
- 수정 후 **위반 0건, 156개 통과, 100점**.

## 4. 검증 및 측정

환경: Windows + WSL Ubuntu, 기존 Python 3.10 가상환경.

| 항목 | 측정값 |
|---|---:|
| 기본 씬 검사 평균 (10회) | 0.0072초 |
| 기본 9개 위반 전체 해결안 조회 | 1.1441초 |
| 엔진 자동 수정 | 0.6056초 |
| 실제 HTTP `/api/autofix` (최종 보완 후) | 0.660초 |

시간은 한 환경의 측정값이며 하드웨어·부하에 따라 달라진다. 회귀 테스트는 자동 수정 **5초 미만**을 확인한다.

테스트는 측정값·대상 쌍·해결안 재검증·네 방향·벽/외곽·침대 측면·경로 안전·원인 추론·호환성·저장 실패·
Undo/Redo·AI 재시도·강제 적용·만료 토큰·동시 변경·place·XSS escape·언어 전환을 포함한다.
실제 HTTP 테스트는 Uvicorn을 임시 포트에 띄워 API를 검증한 뒤 종료한다.
AI 공급자 호출은 대체하여 비밀키나 외부 서비스 없이 실행한다.

현재 환경의 Starlette/httpx 및 AnyIO 조합에서 폐기 예정 경고 2건이 발생한다. 테스트 실패는 아니며 경고를 숨기지 않았다.

최종 UI 통합 후 **pytest 회귀 79개 + 실제 HTTP 1개 = 총 80개 통과, skip 없음**을 확인했다.
프론트엔드 Node 테스트는 WSL에서도 Windows Node 실행 파일을 찾아 언어·escape·확인 적용·리포트를 검증했다.
실제 브라우저에서도 언어 전환, 후보 미리보기, 자동 수정, Undo, 채팅 열기, 한국어/영어 리포트를 확인했다.

## 5. 커밋

| 커밋 | 내용 |
|---|---|
| `021d546` | test: establish deterministic layout regression baseline |
| `afc4853` | feat: add Korean and English presentation across the app |
| `8dbe35f` | fix: preserve original demo when saving layouts |
| `66b9505` | feat: score violations by deterministic clearance shortfall |
| `dc827b2` | feat: inspect directional furniture usage spaces |
| `90d2e53` | feat: calculate clearance-aware circulation paths |
| `e9c155e` | feat: validate AI commands and place furniture deterministically |
| `023ee33` | feat: expand verified resolver search without moving structures |
| `022b1ad` | refactor: align home layout models and preserve legacy scene aliases |
| `73b3187` | fix: ground usage explanations in furniture-specific rules |
| `01f06bc` | feat: refresh workspace with Wanted-inspired responsive design |
| `92c1cd9` | fix: initialize saved-layout availability before enabling restore |
| `d0c1f3a` | fix: localize violation labels in autofix activity |
| 게시 기준 `HEAD` | docs: publish improvement summary and verified example screens |

이 문서와 아래 캡처는 마지막 문서 커밋에 포함된다. 해당 커밋의 해시는 `git log -1 --oneline`으로 확인할 수 있다.

### 실제 프로그램 화면

별도 실행 없이 볼 수 있도록 실제 localhost 앱의 1440×1000 화면을 저장했다.
격리된 Chrome에서 한국어/영어 전환·자동 수정·리포트를 실행했고 브라우저 런타임 오류는 0건이었다.
375, 560, 768, 980, 1200, 1366, 1440px의 실제 뷰포트 너비도 다시 확인했다.
화면 캡처 중 외부 AI 호출이나 개인 배치 저장은 수행하지 않았다.

**기본 검사: 9건·0점**

![한국어 검사](docs/screenshots/01-korean-inspection.png)

**자동 수정: 0건·100점**

![자동 수정 완료](docs/screenshots/02-autofix-success.png)

**English**

![English workspace](docs/screenshots/03-english-workspace.png)

**검토 리포트**

![검토 리포트](docs/screenshots/04-review-report.png)

## 6. 브라우저 확인 체크리스트

- [ ] 데모 초기화 후 위반 9건·0점인지 확인한다.
- [ ] 한국어/English 전환 후 이름·버튼·카드·리포트가 바뀌고 점수는 동일한지 확인한다.
- [ ] 3D 라벨은 괄호 없는 이름이며 사이드바/툴팁에는 읽을 수 있는 이름이 나오는지 확인한다.
- [ ] 책상 앞 빨간 접근 띠와 가구/방문으로 이어지는 파란 동선을 확인한다.
- [ ] 해결안 미리보기와 실제 적용 후 재검사 결과를 확인한다.
- [ ] 전체 자동 수정 후 위반 0건·100점인지 확인한다.
- [ ] Undo로 9건을 복원하고 Redo로 0건이 되는지 확인한다.
- [ ] 저장 → 데모 초기화 → 저장본 복원 순서로 동작하고 두 복원 동작을 Undo할 수 있는지 확인한다.
- [ ] 저장 후 앱을 재시작하면 저장본이 로드되는지 확인한다.
- [ ] 가구 추가 이름이 `침대 2` 같은 한글 이름이며 회전 방향이 앞 접근 띠에 반영되는지 확인한다.
- [ ] AI 연결 환경에서 새 위반 제안이 자동 적용되지 않고, 확인 적용은 AI 재호출 없이 동작하는지 확인한다.
- [ ] 검토 리포트의 위반별 감점·점수 공식·수정 이력과 인쇄 화면을 확인한다.

## 7. 범위와 제한

- 단일 프로세스/공용 작업 씬 기반 로컬 데모이며 다중 사용자용 저장소·인증 기능은 없다.
- 90° 단위 AABB 모델과 100mm 격자 근사를 사용한다. 법적 건축·피난 검토를 대신하지 않는다.
- 탐색은 제한된 후보 내에서만 수행하며 모든 가능한 배치를 찾는다는 보장은 없다.
- AI 설명은 프롬프트와 결정론적 사실로 제한하지만 실제 공급자의 생성 결과 자체를 수학적으로 보장하지 않는다.
- 실제 공급자 통신은 자동 테스트에서 호출하지 않았다. 사용하려면 본인의 제공자 설정이 필요하다.
- `.env`, 개인 저장 배치, 가상환경, 캐시, 원본 Figma 자료는 공개 저장소에 포함하지 않는다.
- 전체 프로그램과 테스트·문서·화면 예시는 `improvements`에 게시하며 기존 `master`는 수정하지 않는다.
