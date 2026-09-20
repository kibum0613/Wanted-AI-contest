# 🏠 AI Home Layout Debugger

> **AI 기반 1인 주택 가구 배치 검증 & 해결 지원 에이전트**
> 기존 인테리어 앱이 배치를 "만들어준다"면, 우리는 당신의 배치를 **디버깅**한다.

가구 배치의 Grammarly. 사용자가 직접 배치한 1인 주택(거실·침실·서재) 레이아웃을 AI가 검사하고 **문제의 원인 · 생활 영향 · 해결 방법 · 유사 사례**까지 제시합니다.

```
Human Layout → AI Critic → Human Revision
```

## 화면과 개선 기록

Wanted Design System 참고 자료의 밝은 표면·선명한 파란색·둥근 컴포넌트·여백을 반영한 반응형 작업 화면입니다.
3D 배경·라벨·사용 공간 표시, 채팅과 검토 리포트까지 같은 시각 체계를 적용했습니다.
375~1440px 화면에서 핵심 제어가 사라지거나 가로로 넘치지 않는지 브라우저로 확인했습니다.
원본 Figma 파일이나 외부 디자인 자산은 저장소에 복사하지 않았습니다.

단계별 변경·설계 이유·측정·커밋·확인 체크리스트는 [IMPROVEMENTS.md](IMPROVEMENTS.md)에 정리했습니다.

아래는 실제 실행한 프로그램의 화면입니다. 목업이나 AI 생성 이미지가 아닙니다.

### 한국어 검사 화면 — 기본 데모 9건·0점

![한국어 기본 씬 검사 화면](docs/screenshots/01-korean-inspection.png)

### 전체 자동 수정 — 5회 수정 후 0건·100점

![자동 수정 완료와 검증 결과](docs/screenshots/02-autofix-success.png)

### English 작업 화면

![English workspace with verified layout](docs/screenshots/03-english-workspace.png)

### 검토 리포트 — 점수·수정 이력·감점 공식

![실제 검토 리포트 화면](docs/screenshots/04-review-report.png)

## 왜 이게 없는가 (시장 조사)

오늘의집 3D, 아키스케치, Planner 5D, Coohom 등 기존 도구는 전부 **생성(Generation) 패러다임** — "AI가 예쁜 배치를 만들어줄게"입니다. 반면:

- ❌ 사용자 배치를 **수치 근거로 검사**해 PASS/FAIL 오류 목록을 주는 도구 없음
- ❌ "옷장이 현관문 개폐 반경을 550mm 침범" 같은 **정량 진단** 없음
- ❌ "소파를 왼쪽 400mm만 옮기면 해소 (부작용 없음, 재검증 완료)" 같은 **검증된 최소 수정** 없음
- ❌ 검출→수정→재검증을 자율 반복하는 **Agent 루프** 없음

좁은 원룸일수록 "예쁘게"보다 **"충돌 없이 살 수 있는가"**가 문제인데, 이 검증 시장이 비어 있습니다.

## 핵심 기능

| | |
|---|---|
| **Detect** | 결정론적 기하 엔진이 가구 겹침 / 문 개폐 구역 침범 / 창문 앞 확보 구역 / 동선 폭 / 가구 사용 공간(책상 750mm 등) / 벽 관통 검사 |
| **Visualize** | Three.js 3D — 위반 하이라이트, 사용 공간 사각형, 자동 계산된 동선 |
| **Recommend** | 해결안 후보를 기하적으로 생성 → **전체 재검증 통과분만** A/B안 제시 + 고스트 미리보기 |
| **Explain + Learn** | LLM이 인체공학 규칙 + 배치 사례 KB 기반으로 원인/영향/추천 근거를 생활 언어로 설명 |
| **Agent** | 기본 데모 9건 → 0건·100점, 새 위반 없는 후보만 적용 (5초 이내 회귀 검사) |
| **Copilot** | 자연어 배치 명령 → 결정론적 위치 탐색·사전 검증·1회 재시도·명시적 강제 적용 |
| **도우미 챗봇** | 인테리어 초보용 Q&A (현재 배치 상태 인지) |
| **편집기** | 가구 드래그(바닥 평면 고정), 동선 경유점 편집, 팔레트 추가/삭제, 속성 편집, Undo/Redo, 저장 |

## 아키텍처 — 역할 분리 원칙

**모든 수치와 판정은 결정론적 엔진에서, LLM은 설명만.**

```
house2.json (원본 데모) / saved_layout.json (사용자 저장본)
    ↓
Geometry + Rule Engine ── 정확한 검출 (LLM 개입 0%)
    ↓
Resolver ── 후보 생성 → 전체 재검증 → 통과분만 제시
    ↓
LLM ── 검증된 사실 + 규칙/사례 KB → 자연어 설명 (수치 생성 금지)
    ↓
사용자 최종 판단 → 적용/실행취소
```

## 실행

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn backend.main:app --port 8001
# → http://localhost:8001
```

Windows PowerShell에서는 활성화 대신 `.venv\Scripts\python.exe`로 위 Python 명령을 실행해도 됩니다.
WSL의 기존 개발 환경은 `source ~/.venvs/wanted-ai-hackathon/bin/activate`로 활성화합니다.
개인용 실행 스크립트 없이도 위 명령으로 전체 프로그램을 실행할 수 있습니다.

선택 사항: `.env.example`을 `.env`로 복사하고 Gemini/Groq/OpenAI API 키 또는 Claude CLI를 설정합니다.
AI가 없어도 검사·해결안·자동 수정·편집은 동작하며, 설명은 엔진 사실에 기반한 템플릿을 제공합니다.
명령·채팅은 AI 연결 실패를 명시합니다. API 키와 개인 저장본은 Git에 포함하지 않습니다.
Three.js는 CDN에서 가져오므로 첫 화면 로드에는 인터넷 연결이 필요합니다.

### 공개 데모 배포·운영 / Public-demo deployment

승인·지역 변경·비용·자원·환경 변수·수동 재배포·운영 책임의 전체 기록은 [서버 배포 기록 (DEPLOYMENT.md)](DEPLOYMENT.md)에 정리했습니다.

공개 앱: **<https://wanted-layout-kibum0613.azurewebsites.net>**. 아래는 실제 배포 설정과 검증 범위입니다.
**현재 상태(2026-09-20): 공개 앱과 실제 AI 설명·채팅·한국어/영어 삭제 명령을 검증했습니다. 배포 코드 `3454627`, 최종 전체 테스트 159개 통과입니다.**
실제 HTTPS 건강 검사 200, 기본 9건·0점 → 자동 수정 5단계·0건·100점(최종 네트워크 포함 **4.289초**),
저장/초기화/복원/Undo/Redo와 브라우저 3D 표시를 확인했습니다. `347529a` 배포 후 Gemini 설명은 3.23초에 정상 구조와 `llm=true`로 응답했습니다.
영어의 정확한 `id=sofa` 삭제는 실제 반영됐습니다. 이전 한국어 CLI 시험은 PowerShell 5의 ASCII 파이프에서
HTTP 전 입력이 물음표로 손상되어 **무효**이며, 서비스/모델의 한국어 제한을 입증하지 않습니다.
올바른 Unicode의 “소파를 삭제해 줘” 요청은 **실제 소파 삭제에 성공**했습니다.
응답 `ops=[{"op":"delete","id":"sofa"}]`와 후속 씬 부재를 확인했고, 명령+씬 조회 합계는 **3.221초**였습니다.
공개 브라우저에서도 한국어 입력·실행 후 소파 사이드바 항목 제거와 WebGL canvas 유지를 확인했고, Demo Reset으로 소파·기본 배치가 복귀했습니다.
Korea Central은 학생 구독 정책으로 거부되어 사용자가 승인한 **Japan East Linux Basic B1, 인스턴스 1개**로 변경했습니다.
자원 그룹은 `rg-wanted-layout-demo`(메타데이터 위치 Korea Central), 플랜은 `asp-wanted-layout-b1`(Japan East)입니다.
안내 비용은 **USD $0.019/시간, 30일 $13.68**(기타 요금/환율/세금 제외)이며 학생 크레딧 만료일은 **2027-08-18**입니다.
spending limit은 On이고 유료 구독으로 업그레이드하지 않았습니다. 앱 중지만으로 플랜 과금이 멈추지는 않습니다.
앱 호스트는 `wanted-layout-kibum0613.azurewebsites.net`이며 Python 3.12, Always On, HTTPS 전용/TLS 1.2 이상, FTP 비활성화로 준비했습니다.
사용자가 Azure 포털에서 Gemini 키를 직접 등록했으며 키는 코드나 문서에 저장하지 않습니다.
최초 일반 `Reply OK` 연결 시험과 실제 앱 통합 검증을 구분하여 기록했습니다.
Azure 등 호스팅 설정에 환경 변수를 등록하고 **인스턴스 1개·worker 1개**로 실행합니다.
`APP_ENV=production` 또는 `LLM_PROVIDER=gemini-free`이면 로컬 `.env`를 읽지 않습니다.

| 환경 변수 | 공개 데모 값 |
|---|---|
| `APP_ENV` | `production` |
| `LLM_PROVIDER` | `gemini-free` |
| `GEMINI_MODEL` | `gemini-3.5-flash-lite` (다른 모델은 설정 오류) |
| `GEMINI_FREE_TIER_ONLY` | `true` (운영자가 무료 프로젝트임을 확인했다는 명시적 승인) |
| `GEMINI_API_KEY` | **결제가 연결되지 않은 무료 Gemini 프로젝트 키**, 호스팅 비밀 설정으로만 전달 |
| `AI_QUOTA_FILE` | `/home/layout-data/ai-quota.json` |
| `SAVED_LAYOUT_PATH` | `/home/layout-data/saved_layout.json` |
| `WEBSITES_ENABLE_APP_SERVICE_STORAGE` | `true` |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `false` (사전 빌드 의존성 포함 ZIP) |
| `ENABLE_ORYX_BUILD` | `false` (상속된 Oryx 활성화도 명시적으로 해제) |
| `PYTHONPATH` 앱 설정 | 없음 — 시작 스크립트가 로컬 runtime 경로를 설정 |

```bash
sh /home/site/wwwroot/start_azure.sh
```

- `scripts/package_azure.py`로 커밋된 소스와 CPython 3.12 Linux wheel을 `app.tar.gz`에 묶습니다.
  ZIP은 압축 payload와 시작 스크립트 두 파일뿐이며, 스크립트가 로컬 디스크에 풀어 **worker 1개·접근 로그 비활성화**로 실행합니다.
- 호스팅 라우팅 포트를 `8000`으로 연결하고 상태 검사 경로를 `/api/health`로 설정합니다.
  Azure App Service의 `/home` 영속 저장소를 활성화하세요
  (`WEBSITES_ENABLE_APP_SERVICE_STORAGE=true`, Linux App Service).
  Python App Service의 실제 코드 실행 위치는 임시 배포 디렉터리일 수 있으므로 코드 옆에 영속 데이터를 저장하지 않습니다.
  배치와 사용량은 위의 절대 `/home/layout-data/` 경로를 그대로 사용해야 재배포·재시작 때 유지됩니다.
  최초 Oryx SDK 추출과 개별 파일 복사 정체 조사 후 단일 압축 runtime 방식으로 전환했습니다.
  `SCM_DO_BUILD_DURING_DEPLOYMENT=false`, `ENABLE_ORYX_BUILD=false` **둘 다**를 사용하고 고정 `PYTHONPATH` 앱 설정은 제거합니다.
  한 설정만 끄면 상속된 Oryx 설정 때문에 원격 빌드가 계속 실행될 수 있습니다.
  현재 성공한 배포 명령은 현대식 `az webapp deploy`입니다.
  패키징·설정·상태 확인 절차와 이전 deprecated ZipDeploy 조사 이력은 [DEPLOYMENT.md](DEPLOYMENT.md)를 따릅니다.
  **자동 확장·다중 인스턴스·다중 worker·reload·동시에 실행하는 배포 슬롯은 사용하지 않습니다.**
- 건강 검사는 실제 Google 요청을 하지 않습니다. 설정·사용량 파일·저장 폴더의 쓰기 가능 여부를 검사하며,
  잘못된 설정/손상 파일/저장 실패는 시작 실패 또는 HTTP 503으로 드러납니다. 오류를 숨기고 사용량을 초기화하지 않습니다.
- 실제 제공자 호출을 모든 AI 기능이 공유하며 **최근 60초 최대 10회·최근 24시간 최대 400회·동시 1회**입니다.
  24시간 이동 창은 제공자 달력 날짜의 일일 한도보다 보수적입니다. 명령의 엔진 검증 재시도(최대 1회)도 별도 차감합니다.
  HTTP 오류·시간 초과·안전 필터·잘못된 응답도 차감하고 환급하지 않습니다. 확인 적용·검사·자동 수정·캐시 적중은 호출하지 않습니다.
- 파일 lock + 원자적 교체 + `fsync`로 호출 **전에** 시각을 저장합니다. 재시작해도 한도가 유지됩니다.
  SQLite/WAL은 사용하지 않습니다. 파일 시스템의 잠금·원자적 rename·`fsync` 지원이 필요합니다.
  호출 직전 프로세스가 종료되면 실제 호출 없이 1회 차감될 수 있습니다(한도 초과보다 안전한 방향).
  **사용량 파일/lock 파일을 삭제하거나 경로를 변경하거나 과거 백업으로 되돌리지 마세요.**
  손상 시 운영자가 점검해야 하며 마지막 호출 후 24시간이 지나기 전에는 새 빈 파일로 초기화하지 않습니다.
- `gemini-free`는 오직 지정된 Gemini REST 모델만 사용합니다. 자동 네트워크 재시도, 다른 모델,
  Groq/OpenAI/Claude, 템플릿으로의 조용한 대체는 없습니다. `thinkingConfig`는 지정하지 않습니다.
  **API 키만으로 결제 여부를 판별할 수 없으므로 무료 전용 프로젝트에서 Cloud Billing을 연결하지 않아야 합니다.**
  코드의 `GEMINI_FREE_TIER_ONLY=true`는 결제를 기술적으로 끄는 스위치가 아닙니다.
- AI 분석·명령은 `responseMimeType=application/json`과 기능별 `responseSchema`로 구조화된 출력을 요청합니다.
  챗봇은 일반 텍스트를 유지합니다. `MAX_TOKENS` 응답은 `ai_output_truncated`로 명시하고,
  JSON 파싱 가능 여부와 관계없이 잘린 명령을 적용하거나 성공으로 간주하지 않습니다.
  명령의 빈 작업 목록도 성공으로 처리하지 않습니다. 기존 1회 재시도 안에서 다시 제안받고,
  여전히 작업이 없으면 `ai_no_action` 오류를 반환합니다. 서버가 사용자 문장을 정규식으로 해석해 AI 작업을 대신 만들지는 않습니다.
  AI 문맥에는 객체의 저장 이름·표시 이름·짧은 이름과 정확한 ID, 한국어/영어 가구 종류 대응표를 함께 제공합니다.
  AI가 이름을 실제 ID에 대응시켜 작업을 제안하며, 없는 ID를 이름/종류로 대신 해석하거나 임의 생성하여 적용하지 않습니다.
- 요청 본문 최대 128 KiB, 질문/명령 1~500자, 대화 기록 최대 8개(각 300자),
  내부 프롬프트 최대 24,000자/64,000 UTF-8 bytes, 출력 최대 4,096 tokens/12,000자,
  제공자 응답 최대 64 KiB, 소켓 대기 최대 60초입니다.
  공개 씬은 총 객체 100개, ID 80자/이름 120자, 좌표 절댓값 30m,
  동선당 경유점 2~100개, 규칙/동선 폭 10,000mm 이하로 제한합니다.
- API는 `detail`(선택 언어), `code`, 필요 시 `retry_after`와 `Retry-After`를 반환합니다.
  429는 공용 사용량/동시 요청/제공자 한도, 503은 설정·연결·저장소 오류,
  502는 제공자/응답 오류, 504는 시간 초과, 413/422는 크기/입력 오류입니다.
  AI 분석·명령·채팅 UI 모두 한국어/영어 오류를 그대로 표시하며 키·프롬프트·제공자 오류 본문은 로그에 출력하지 않습니다.
- 공개 데모는 **인증 없는 공용 씬**입니다. 다른 방문자가 편집·저장·초기화할 수 있습니다.
  개인별 프로젝트 격리·인증·방문자별 속도 제한·전체 CPU 작업 한도는 제공하지 않으므로 악의적 트래픽 대응은 호스팅 계층에서 해야 합니다.
  Undo/Redo와 작업 이력은 메모리에만 있고, 명시적 **저장**만 재시작 후 복구됩니다.
- 무료 Gemini에는 배치·질문·최근 대화가 전송됩니다. Google은 입력/응답을 제품 개선에 사용하고
  사람이 검토할 수 있으므로 **개인정보·기밀·민감정보를 입력하지 마세요**.
  UI에도 양언어로 고지합니다. 지역별 예외와 이용 조건은
  [공식 Gemini API 약관](https://ai.google.dev/gemini-api/terms)을 확인하세요.

**English summary:** The user approved provisioning after verifying student credit.
Japan East Linux Basic B1 resources now exist; Korea Central was rejected by subscription policy.
The public UI, deterministic engine, persistence flows, structured AI explanation, English chat, and Korean/English deletion commands were verified.
Earlier Korean CLI probes were invalid: PowerShell 5's ASCII pipe corrupted the input before HTTP.
They do not demonstrate a Korean-language limitation. A Unicode-preserving retry successfully deleted the sofa, confirmed in the actual scene.
Use a non-billed Gemini project, the exact model and settings above, one worker/instance, and durable `/home` storage.
Shared AI limits are 10 calls/minute and 400/rolling 24 hours; retries and failed attempts count separately.
There is no paid/provider fallback. The public scene is shared and unauthenticated; do not submit personal or sensitive data.
Free Gemini inputs/outputs may be used for product improvement and human review under Google's terms.
For local legacy provider priority/fallback, explicitly set `APP_ENV=local` and `LLM_PROVIDER=legacy`
(the backward-compatible local default); production refuses that selection.

## 테스트

### 표시 언어

화면의 언어 선택에서 한국어(기본값)와 English를 전환할 수 있습니다. 선택은 브라우저에 보관됩니다.
API는 `?lang=ko` 또는 `?lang=en`으로 위반 설명·해결안·AI 응답의 언어를 선택합니다.
언어는 표시만 바꾸며, ID·좌표·측정값·판정·점수는 동일합니다. 가구의 저장 이름은 한국어를 유지하고
3D 라벨에서는 괄호 설명을 생략합니다. 사용자 입력 이름이나 이전 대화 기록은 자동 번역하지 않습니다.
AI 응답은 HTML로 실행하지 않고 텍스트로 표시합니다.

### 회귀 테스트 실행

공개 배포 준비 회귀 결과: 기존 80개를 포함한 **142 tests passed**.
이후 구조화 AI 응답 수정본은 **전체 pytest 153개 통과**(기존 경고 2개, 13.11초)했습니다.
WSL Windows `.exe` 실행 오류를 피해 checksum 검증한 격리 Linux Node.js 24.18을 사용했고 프로젝트 의존성은 추가하지 않았습니다.
이름 문맥 보완본은 관련 테스트 **114개**, 최종 전체 테스트 **159개 통과**(기존 경고 2개, **13.57초**, skip 없음)입니다.
이전 한국어 CLI 시험의 ASCII 입력 손상을 바로잡은 실제 한국어 요청도 삭제 작업과 씬 반영까지 확인했습니다.
제공자 호출은 테스트 가짜 전송기로 대체하며 무료 할당량/실제 키를 사용하지 않습니다.
기본 데모 9건 → 자동 수정 0건·100점 및 Node 기반 한국어/영어 UI 검사를 유지합니다.

저장은 원본 데모가 아닌 `backend/data/saved_layout.json`에 기록됩니다(버전 관리 제외).
앱 시작 시 저장본이 있으면 불러옵니다. **저장본 복원**과 **데모 초기화**는 모두 Undo/Redo가 가능하며,
데모 초기화는 저장 파일을 지우지 않습니다. 저장본이 없으면 복원 버튼은 비활성화됩니다.

프로젝트 루트에서 실행합니다. WSL에서는 기존 가상환경을 먼저 활성화합니다.

```bash
source ~/.venvs/wanted-ai-hackathon/bin/activate  # WSL에서 실행할 때
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

WSL 공유 드라이브에서 pytest 캐시 권한 경고가 발생하면 `python -m pytest -q -p no:cacheprovider`로 실행합니다.
실제 HTTP 검증만 실행하려면 `python -m pytest -q -s -p no:cacheprovider tests/test_live_api.py`를 사용합니다.
이 테스트는 충돌하지 않는 로컬 포트에 Uvicorn을 시작하여 API를 확인하고 종료합니다.

개발 의존성은 `pytest`와 FastAPI `TestClient`에 필요한 `httpx`입니다.
테스트는 LLM을 호출하지 않으며 API 작업 상태와 데이터 경로를 격리하여 원본 데모를 변경하지 않습니다.
프론트엔드 JavaScript 검증에는 Node.js가 필요합니다(없으면 해당 테스트만 skip).

현재 [기본 데모](backend/data/house2.json)의 기준선은 **9건 (HIGH 6건, MEDIUM 3건), 0점**입니다.
부족량은 `max(요구 − 실측, 0)` mm이며 감점은 HIGH `10 + min(10, 부족량/50)`,
MEDIUM `4 + min(6, 부족량/50)`입니다. 50mm마다 1점을 추가하되 개별 위반의 감점을 20/10점으로 제한하여
침범 깊이를 구분하면서 한 위반이 전체 점수를 지배하지 않도록 했습니다. 소수 첫째 자리로 반올림한 감점의 합을
100에서 빼며 최저 점수는 0점입니다.

| 코드 | 대상 a | 대상 b |
|---|---|---|
| HARD_CLASH | sofa | table |
| HARD_CLASH | tv_stand | wall_b |
| ZONE_INTRUSION | bed | bedroom_window |
| ZONE_INTRUSION | wardrobe | bedroom_door_swing |
| USAGE_SPACE | desk | bookshelf |
| OUT_OF_ROOM | tv_stand | living |
| CIRCULATION | bedroom_door_swing | wardrobe |
| CIRCULATION | bed | wardrobe |
| CIRCULATION | wardrobe | wardrobe |

동선 검사 도입 전의 기존 위반 6건은 유지됩니다. 옷장이 침실 입구를 막아 방문·침대·옷장 앞까지 접근하지 못하는
동선 위반 3건이 새로 드러났습니다. 마지막 행은 옷장 자신의 위치가 그 앞 접근을 막는 경우입니다.

[회귀 테스트](tests/test_baseline.py)는 코드·대상 쌍·측정값, 각 위반의 1순위 해결안 적용 후 대상 위반 해소와 새 위반 없음,
`/api/autofix` 후 **0건·100점**, 반복 실행과 Undo/Redo를 검증합니다.
규칙이나 의도된 위반이 바뀌면 기준선과 테스트를 함께 갱신합니다.

## 검사 규칙 (기본값)

| 규칙 | 기준 | 근거 |
|---|---|---|
| 주 동선 폭 | 600mm (권장 900) | 1인 통행 + 물건 운반 |
| 문 개폐 구역 | 침범 금지 | 출입/피난/가구 반입 |
| 창문 앞 확보 | 침범 금지 (~500mm) | 채광/환기/결로/피난 |
| 책상 사용 공간 | 750mm | 의자 빼고 앉는 동작 |
| 옷장 개폐 공간 | 600mm | 여닫이 문짝 폭 |
| 냉장고·세탁기 앞 공간 | 600mm | 문 개폐와 물품 접근 |
| 침대 긴 측면 | 두 측면 중 하나 300mm 이상 | 승하차·침구 정리 |
| 가구 겹침/벽 관통 | 금지 | 물리적 배치 가능성 |

사용 공간은 앞면의 폭 구간에 걸치는 가구·벽·건물 외곽까지 측정하며, 구역과 바닥은 장애물에서 제외합니다.
회전은 Z축 반시계 방향으로 `0°=-Y`, `90°=+X`, `180°=+Y`, `270°=-X`입니다.
기본 데모 책상은 남쪽 벽에서 방 안을 바라보도록 180°로 수정했습니다. 다른 가구는 기존 0° 방향을 유지합니다.
책상–책장 400mm 위반을 포함한 6건은 유지하며, 기존 `MAINTENANCE_SPACE` 코드는 `USAGE_SPACE`로 변경했습니다.
`maintenance_clearance_mm`은 타입 기본값을 덮어씁니다(0은 검사 비활성화).
바닥의 반투명 초록/빨강 사각형은 각 접근 면의 통과/부족 상태를 나타냅니다.

### 자동 동선 검사

바닥 100mm 격자의 셀 중심에서 가구·벽·건물 외곽까지 300mm 미만인 곳을 막습니다.
NumPy가 장애물 마스크를 계산하고 현관에서 4방향 BFS를 한 번 수행합니다. 각 방문과 사용 공간 가구 앞이 목표이며
침대는 어느 긴 측면이든 도달하면 통과합니다. 사람 중심이 설 수 있도록 가구 앞 목표 띠의 깊이는 최소 600mm입니다.
성공 경로는 바닥의 파란 선으로 표시합니다. 실패하면 가구를 하나씩 제거한 상태로 도달성을 검사해 원인을 지정합니다.
단일 가구 제거로 해결되지 않으면 고정 구조/여러 장애물로 명시합니다.
구조물 `role`은 `entrance`, `door`, `window`이며, 옛 데이터는 ID에서 추론합니다.
현관이 없는 옛 씬은 동선 검사를 비활성화하고 API에 이유를 반환합니다.

후보 검증 때는 경로 좌표 생성만 생략하며 동일한 판정을 수행합니다. 가구 제거 시 기존 BFS 도달 영역을 재사용합니다.
자동 수정은 새 위반 없는 후보만 사용하고, 잔여 위반 수를 우선 줄이는 후보를 고릅니다.
도입 시 실제 HTTP 자동 수정은 **9건 → 0건·100점, 약 1.91초**였으며 회귀 테스트의 제한은 5초입니다.

### AI 명령의 적용 전 검증

AI가 제안한 작업은 복사본에 일괄 적용하여 검사합니다. 새 위반이 생기면 원본은 변경하지 않고
위반 내용을 피드백하여 한 번만 재시도합니다. 재시도에도 위반이 있으면 **새 위반 N건**과 **그래도 적용**을 표시합니다.
확인 버튼은 서버에 보관된 동일 작업 결과만 적용하며 AI를 다시 호출하지 않습니다.
다른 편집이나 Undo/Redo 후에는 확인 토큰이 만료됩니다. 잘못된 작업 목록은 부분 적용하지 않습니다.

`place`는 `id` 또는 `type` 중 하나와 `room`, 선택적 `near`를 받습니다.
엔진이 100mm 격자 × 4방향 후보를 만들고 충돌·방 경계·사용 공간을 빠르게 거른 후 거리순으로
최대 64개 후보를 전체 검사합니다. 새 위반 없는 첫 위치만 적용하며, 찾지 못하면 명시적인 오류를 반환합니다.
AI 프롬프트는 `place`를 우선하도록 하며 좌표 계산은 엔진이 담당합니다.

### 해결안 탐색

벽과 구역 등 구조물은 이동 후보에서 제외합니다. 축 이동과 90/180/270° 회전을 먼저 검사하고,
깨끗한 후보가 2개 미만이면 대각선 이동과 회전+이동 조합까지 확장합니다.
저렴한 기하 검사에서 새 충돌·구역 침범·이탈·사용 공간 위반을 먼저 거른 뒤 전체 동선을 재검사하므로
탐색 폭을 늘려도 속도를 유지합니다. 새 위반을 만드는 완화 후보는 더 이상 표시하지 않습니다.
확장 후 기본 씬의 9개 위반 전체 해결안 조회는 약 **1.06초**, 실제 HTTP 자동 수정은 약 **0.61초**였습니다.

## 프로젝트 구조

```
backend/
├── main.py          # FastAPI + Undo/Redo + Auto-Fix Agent
├── models.py        # Scene/가구/구역/동선 데이터 모델
├── geometry.py      # 기하 계산 (선분-박스, 박스-박스 거리)
├── detector.py      # Rule Engine (ZONE_INTRUSION 등 주거 특화)
├── usage.py         # 회전·벽·건물 외곽을 고려한 접근 면 검사
├── circulation.py   # NumPy 점유 격자 + BFS 동선/장애물 판정
├── resolver.py      # 해결안 생성 + 재검증 (바닥 평면 제약)
├── placement.py     # 100mm × 4방향 결정론적 place 탐색
├── i18n.py          # 한국어 조사·이름·방향·영문 메시지
├── llm.py           # LLM 프로바이더 (Gemini/Groq/OpenAI/Claude CLI)
├── commands.py      # 자연어 → 배치 작업(ops)
├── chat.py          # 배치 도우미 챗봇
└── data/
    ├── house2.json     # 기본 데모 (의도된 기존 6건 + 동선 3건)
    ├── house.json      # 이전 주택 씬 (읽기 호환 유지)
    ├── studio.json     # 이전 원룸 씬 (읽기 호환 유지)
    └── knowledge.json  # 인체공학 규칙 + 배치 사례 KB
frontend/
└── index.html       # Three.js 뷰어 + 전체 UI
tests/               # 기하·규칙·해결안·저장·AI 검증·실제 HTTP·JS 테스트
requirements-dev.txt # 테스트 의존성
```

## 호환성과 API

Python 모델은 `Furniture`, `Walkway`, `Scene.furniture`, `Scene.walkways`를 사용합니다.
이전 `Equipment`, `Pipe` 클래스와 `.equipment`, `.pipes` 접근은 호환용 별칭으로 남깁니다.
Pydantic은 새 키와 옛 키를 모두 읽으며, 저장/API JSON은 기존 `equipment`, `pipes` 키를 유지합니다.
위반 대상 kind는 `furniture`, `walkway`, `structure`, `room`입니다.
면이 닿기만 하는 깊이 0의 경우 충돌로 처리하지 않습니다.

| API | 용도 |
|---|---|
| GET/PUT `/api/scene` | 작업 씬 조회/편집 |
| GET `/api/inspect`, `/api/resolve/{id}` | 검사 및 검증된 해결안 |
| POST `/api/apply`, `/api/autofix` | 해결안/자동 수정 |
| POST `/api/save`, `/api/restore`, `/api/reset` | 저장/저장본 복원/원본 데모 |
| GET `/api/storage` | 저장본 존재 여부 |
| POST `/api/undo`, `/api/redo` | 실행취소/재실행 |
| POST `/api/command`, `/api/command/apply` | AI 제안 검증/거부된 동일 작업 확인 적용 |
| GET `/api/explain/{id}`, POST `/api/chat` | AI 설명/질문 |
| GET `/api/report` | 점수·위반·변경 이력 |

### 범위와 제한

- 한 프로세스의 공용 작업 씬을 사용하는 로컬 데모이며, 다중 사용자 서비스가 아닙니다.
- 회전은 90° 단위 AABB 모델입니다. 동선은 100mm 격자 근사이며 법적 피난·건축 검토를 대신하지 않습니다.
- 해결안·place는 제한된 후보 탐색입니다. 해결 불가능한 경우 원본을 바꾸지 않고 수동 검토/실패를 알립니다.
- AI 네트워크 호출은 테스트에서 대체합니다. 실제 공급자 연결과 생성 문구는 환경에 따라 달라집니다.

## 계보

같은 아키텍처의 조선 도메인 버전에서 출발: [K-Shipbuilding-AI-Hackathon](https://github.com/GeunheePARKKK/K-Shipbuilding-AI-Hackathon) (AI Ship Design Debugger — 기관실 배관/장비 간섭 검증). 도메인 독립적 코어(기하/규칙/해결안/Agent)를 재사용하고 규칙·데이터·프롬프트만 교체해 이식.
