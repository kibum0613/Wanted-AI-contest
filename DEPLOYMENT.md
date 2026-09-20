# 서버 배포 기록 및 운영 안내

> **상태: 공개 배포 및 한국어/영어 실제 AI·결정론적 기능 검증 완료** — 2026-09-20
>
> 공개 앱·3D·결정론적 검사/자동 수정·저장/복원·실제 Gemini 설명/채팅·명시적 영어 ID 삭제를 확인했다.
> **이전 한국어 CLI 시험은 PowerShell 5의 ASCII 파이프에서 입력이 손상되어 무효다.** 서비스/모델의 한국어 이해 제한을 입증하지 않는다.
> 배포 코드 `3454627`에서 Unicode를 보존한 한국어 삭제 요청도 실제 소파 삭제까지 확인했다.
> 최종 전체 테스트는 **159 passed**, 기존 경고 2개, **13.57초**, 건너뛴 테스트 없음이다.

- 저장소: [kibum0613/Wanted-AI-contest](https://github.com/kibum0613/Wanted-AI-contest)
- 작업·기록 브랜치: **`improvements`** — 별도 저장소를 만들지 않았다.
- 공개 앱: **<https://wanted-layout-kibum0613.azurewebsites.net>**
- 건강 검사: <https://wanted-layout-kibum0613.azurewebsites.net/api/health?lang=en>
- 관련 문서: [README](README.md), [개선 결과](IMPROVEMENTS.md), [변경 이력](CHANGELOG.md)

이 문서에는 공개 가능한 설정·판단·검증 결과만 기록한다. API 키, 구독/테넌트 식별자, 이메일, 개인 크레딧 잔액은 포함하지 않는다.

## 1. 승인부터 공개 검증까지

| 순서 | 진행 내용 | 결과 / 판단 |
|---|---|---|
| 1 | 기존 개선 브랜치에서 공개 배포 전제 구현 | 무료 Gemini 전용 경로, 공용 사용량 제한, 외부 영속 파일, 건강 검사, 입력 제한, 양언어 개인정보 안내 |
| 2 | 학생 구독 조건 확인 | `AzureForStudents`, **spending limit On** 확인. 유료 종량제 구독으로 업그레이드하지 않음 |
| 3 | Korea Central Linux Basic B1 방향 검토 | 사용자가 잔액을 확인하는 동안 자원 생성을 보류 |
| 4 | 사용자가 크레딧 확인 후 비용·자원 생성 승인 | 만료일 **2027-08-18** 확인. 개인 잔액은 공개 기록에서 제외 |
| 5 | Korea Central 컴퓨팅 자원 생성 시도 | 학생 구독 지역 정책으로 거부 |
| 6 | 허용 지역 중 Japan East와 변경 단가 안내 | 사용자가 **Japan East Linux Basic B1** 승인. 정책 해제/권한 우회가 아니라 **허용된 지역으로 변경** |
| 7 | 그룹·플랜·앱 준비 | Python 3.12, 인스턴스 1개, Always On, HTTPS/TLS 1.2, FTP 비활성화 |
| 8 | 사용자 직접 Gemini 키 등록 | Azure 포털 앱 설정에 입력. 키를 대화/Git로 전달하지 않았고 존재 여부만 불리언 확인 |
| 9 | 별도 실제 Gemini 연결 시험 | 일반 `Reply OK` 요청, 출력 상한 32 tokens, thinking 설정 없음 → `OK`, 총 8 tokens. 개인 코드/민감정보 전송 없음 |
| 10 | 애플리케이션 사전 검증 | 기존 80개를 포함한 **142 tests passed**, 로컬 HTTP 9건 → 0건·100점 |
| 11 | 소스 ZIP/Oryx 원격 빌드 시도 | 최초 게이트웨이 502 후 기존 작업을 추적. SDK 추출 정체, Kudu 재시작 후 남은 빌드 프로세스 없음 |
| 12 | wheel을 개별 파일로 포함한 ZIP 시도 | 빌드 설정 두 개를 명시적으로 끄고 ZipDeploy 기본 복사 동작 확인. 이후 복사도 정체되어 원인 단정 없이 조사 |
| 13 | 압축 runtime 패키징으로 변경 | 소스와 Linux wheel을 **단일 `app.tar.gz` + 시작 스크립트**로 묶어 공유 볼륨의 대량 파일 복사를 피함 |
| 14 | compact ZIP을 현대식 `az webapp deploy`로 배포 | 성공. 최초 compact 배포 빌드 8초, 후속 배포 빌드 1초/기동 81초; `RuntimeSuccessful`, 성공 인스턴스 1/실패 0 |
| 15 | 실제 HTTPS·브라우저 검증 | 건강 검사 200, UI/3D, 검사/자동 수정, 저장/초기화/복원/Undo/Redo 확인 |
| 16 | 실제 AI 오류 조사 및 구조화 출력 수정 | 최초 설명 502, 별도 진단은 정상 JSON. 응답 스키마를 강제하고 잘린/빈 명령은 명시적으로 거부 |
| 17 | `347529a` 수정본 공개 검증 | 설명 3.23초·`llm=true`, 영어 채팅, 명시적 영어 `id=sofa` 삭제 실제 성공 |
| 18 | 한국어로 의도한 CLI 시험 | 빈 작업 오류를 관찰했으나, 이후 실제 HTTP 전 입력이 ASCII 파이프에서 물음표로 바뀐 것을 확인. **한국어 시험 증거로 무효** |
| 19 | 이름 문맥 보완 | `_brief`에 원래/표시/짧은 이름과 실제 ID, 양언어 종류명을 추가. 명확성/사용자 지정 이름 지원 개선이며 모델의 한국어 약점을 입증한 수정은 아님 |
| 20 | 입력 보존 진단 및 수정본 배포 | `ascii(text)`와 의도한 Unicode 값 비교로 하네스 손상 확인. 전체 159개 테스트 통과, `3454627` 배포 성공(78초). Unicode escape로 입력을 보존하여 다음 단계 재시험 수행 |
| 21 | 올바른 Unicode 한국어 실제 시험 | “소파를 삭제해 줘” → 삭제 응답/작업/실제 씬 부재 확인. 명령과 후속 씬 조회 합계 **3.221초** |
| 22 | 최종 회귀·데모 상태 정리 | 전체 **159 passed**, 기존 경고 2개, 13.57초, skip 없음. HTTP 자동 수정 **5 actions, 9→0건·100점, 4.289초**. 작업 화면 기본 9건으로 복귀, 100점 저장본 유지 |
| 23 | 공개 브라우저 한국어 end-to-end | 한국어 선택 → 실제 Unicode “소파를 삭제해 줘” 입력/실행 → 사이드바 소파 항목 제거·WebGL canvas 유지 확인. Demo Reset 클릭 후 소파와 기본 배치 복귀 |

주요 커밋: `048d649` 배포 전제, `9c04de0` compact runtime 패키징, `6bdc10b` WSL 체크아웃 패키징 호환,
`347529a` 구조화 Gemini 응답/빈 계획 거부, `3454627` 이름·ID 문맥 개선.
마지막 커밋의 배포 성공과 인코딩을 보존한 한국어 실제 호출 성공을 각각 확인했다.

## 2. 실제 자원 및 최종 실행 설정

| 항목 | 값 |
|---|---|
| Resource Group | `rg-wanted-layout-demo` |
| 그룹 메타데이터 위치 | Korea Central |
| App Service Plan | `asp-wanted-layout-b1` |
| 실제 컴퓨팅 지역 | **Japan East** |
| OS / SKU / 용량 | Linux / **Basic B1 / 1 instance** |
| Web App | `wanted-layout-kibum0613` |
| Python | **3.12** |
| Always On | 활성화 |
| HTTPS Only / 최소 TLS | 활성화 / **1.2** |
| FTP | 비활성화 |
| 건강 검사 | `/api/health` |
| 앱 내부 포트 / worker | **8000 / 1** |

그룹 메타데이터 위치와 실제 플랜 실행 지역은 다르다. 이 앱의 컴퓨팅 자원은 Japan East에 있다.

**최종 App Service 시작 명령:**

```text
sh /home/site/wwwroot/start_azure.sh
```

저장소의 `scripts/start_azure.sh`는 ZIP 안에서 루트 `start_azure.sh`가 된다.
`/home/site/wwwroot/app.tar.gz`를 로컬 임시 runtime 디렉터리에 풀고, 그 내부의 Python 의존성 경로를
`PYTHONPATH`로 설정한 뒤 아래 프로세스를 `exec`한다.

```text
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 1 --no-access-log
```

임시 runtime은 재생성 가능한 코드/의존성 전용이며 영속 상태를 저장하지 않는다.
교체 도중 잠시 사용한 빈 디렉터리의 `http.server`는 임시 진단용이었고 **최종 서비스가 아니다**.
자동 확장·다중 인스턴스·다중 worker·`--reload`·동시에 서비스하는 배포 슬롯은 지원 범위가 아니다.

## 3. 최종 환경 변수와 비밀 관리

| 환경 변수 | 값 |
|---|---|
| `APP_ENV` | `production` |
| `LLM_PROVIDER` | `gemini-free` |
| `GEMINI_MODEL` | `gemini-3.5-flash-lite` |
| `GEMINI_FREE_TIER_ONLY` | `true` |
| `GEMINI_API_KEY` | `<Azure 포털에 등록한 무료 프로젝트 키>` — 실제 값은 공개하지 않음 |
| `AI_QUOTA_FILE` | `/home/layout-data/ai-quota.json` |
| `SAVED_LAYOUT_PATH` | `/home/layout-data/saved_layout.json` |
| `WEBSITES_ENABLE_APP_SERVICE_STORAGE` | `true` |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | **`false`** |
| `ENABLE_ORYX_BUILD` | **`false`** |
| `PYTHONPATH` 앱 설정 | **없음** — 시작 스크립트가 로컬 runtime에 맞게 설정 |

- 두 빌드 플래그를 **모두** 명시한다. 실제로 첫 플래그만 끄면 상속된 `ENABLE_ORYX_BUILD=true` 때문에 Oryx가 실행됐다.
- 키는 포털에서 등록한 값을 유지한다. 예제 자리표시자로 덮어쓰거나 Git/로그에 저장하지 않는다.
- 앱 설정 전체 출력, `printenv`, 인증 헤더/요청 본문 출력으로 비밀을 노출하지 않는다.
- `production`/`gemini-free`는 로컬 `.env`를 읽지 않는다.
- `GEMINI_FREE_TIER_ONLY=true`는 운영자의 무료 프로젝트 확인 표시다. Google 결제를 끄는 API 설정이 아니므로
  **Gemini 프로젝트에 Cloud Billing을 연결하지 않는 것**은 운영자가 별도로 지켜야 한다.
- 지정 모델 실패 시 다른 Gemini 모델, Groq/OpenAI/Claude, 유료 제공자로 전환하지 않으며 오류를 템플릿 성공으로 숨기지 않는다.

## 4. 비용, 크레딧, 중지와 삭제

Japan East Linux Basic B1의 안내 단가는 **USD $0.019/시간**이다.

```text
0.019 × 24시간 × 30일 = USD $13.68 / 30일
```

플랜 1개·인스턴스 1개를 30일 연속 사용하는 계산이다. 월 정액/실제 청구 보장이 아니며 월 일수, 환율, 세금,
추가 자원, 네트워크·저장소·모니터링 등 별도 요금과 가격 변경은 포함하지 않았다.

- 학생 크레딧 만료일: **2027-08-18**. 개인 잔액과 잔액으로 환산한 남은 일수는 기록하지 않는다.
- 확인된 **spending limit On**, 이번 작업에서 유료 구독으로 업그레이드하지 않았다.
- 서버는 유료 SKU를 학생 크레딧으로 사용하는 것이며 영구 무료 호스팅이 아니다.
- 플랜 생성 이후에는 코드 미배포·방문자 없음·배포 조사 중에도 과금될 수 있다.
- Azure 학생 구독과 Google Gemini 프로젝트의 무료 여부는 별개다.
- spending limit은 앱별 비용 모니터링/알림을 대신하지 않는다. 크레딧 만료/소진에 따른 서비스 중단 가능성도 확인한다.

| 작업 | 비용상 의미 |
|---|---|
| Web App 중지 / Always On 해제 | 요청 처리/절전 동작만 변경. **Basic 플랜 비용은 계속 발생** |
| Web App만 삭제 | 남아 있는 플랜 비용은 계속 발생할 수 있음 |
| 전용 플랜 삭제 | 해당 플랜의 향후 컴퓨팅 비용 중단. 공유 앱 유무 확인/백업/승인 필요 |
| 전용 리소스 그룹 삭제 | 포함 자원 일괄 삭제. 보존할 자원 여부 확인 및 별도 승인 필요 |

**이 문서나 배포 승인은 삭제 승인이 아니다.** 데모 종료 시 필요한 자료를 비공개 위치에 백업하고,
별도 승인을 받아 전용 자원을 정리한 뒤 잔여 자원/지연 집계 비용을 확인한다.

## 5. Gemini 무료 한도와 명령의 안전성

| 구분 | RPM | 일일 한도 | 기타 |
|---|---:|---:|---|
| 실제 AI Studio 계정에서 확인한 지정 모델 무료 한도 | **15** | **500 RPD** | **250,000 TPM**, 확인 시점 기준 |
| 앱이 허용하는 전체 방문자 공용 예산 | **10 / 최근 60초** | **400 / 최근 24시간** | **동시 실제 호출 1개** |

제공자 한도는 계정·프로젝트·시점별로 달라질 수 있으며 모든 계정에 대한 보장이 아니다.
앱의 이동 24시간 한도는 달력 날짜 기준보다 보수적이다.

- 분석·명령·채팅이 같은 예산을 공유한다. 사용자마다 400회가 아니다.
- 전송 **전에** 파일에 사용량을 저장한다. 실패·시간 초과·잘못된 응답·명령 재시도도 각각 차감한다.
- 명령 검증/빈 계획 재시도는 최대 1회. 각 실제 호출은 별도 차감하며, 재시도 한도 부족 시 부분 적용하지 않는다.
- 명령 확인 적용, 결정론적 검사/자동 수정, 설명 캐시 적중은 제공자 호출을 하지 않는다.
- 관리자 직접 시험이나 다른 서비스의 Google 호출은 앱 파일에 자동 반영되지 않는다. 같은 프로젝트의 외부 소비자를 주의한다.
- 파일 lock + 원자적 교체 + `fsync`; SQLite/WAL은 사용하지 않는다. 손상·쓰기 실패·시계 역행은 명시적으로 차단한다.
- 사용량 파일/lock 삭제, 경로 변경, 과거 백업 복원으로 한도를 초기화하지 않는다.
- 요청 500자, 대화 8×300자, 본문 128 KiB, 프롬프트 24,000자/64,000 bytes,
  출력 4,096 tokens/12,000자, 제공자 응답 64 KiB 등의 상한을 유지한다. thinking 설정은 명시하지 않는다.
- 분석/명령은 `responseMimeType=application/json`과 기능별 `responseSchema`를 사용한다. 채팅은 일반 텍스트다.
- 잘린 응답은 `ai_output_truncated`, 반복된 빈 작업은 `ai_no_action`으로 실패한다.
  “완료”라는 AI 문장만으로 실제 작업 성공이라고 판단하지 않는다.
- 이름 문맥 보완본은 원래/표시/짧은 이름과 정확한 ID를 제공한다. 서버가 한국어 문장을 정규식으로 해석해
  대신 작업을 만들거나, 없는 ID를 이름/종류로 자동 치환하지 않는다. 모든 실제 변경은 기존 엔진 검증을 거친다.

429는 공용/제공자 한도 또는 동시 요청, 503은 설정·저장소·연결, 502는 제공자/응답/무작업,
504는 시간 초과, 413/422는 크기/입력 오류다. 오류 메시지는 한국어/영어로 표시한다.
**좌표·측정·위반·점수·해결 가능 여부는 결정론적 엔진이 계산한다.**

## 6. 공용 데모와 개인정보

- 로그인/개인별 프로젝트 격리가 없는 **공용 씬**이다. 모든 방문자가 편집·저장·초기화할 수 있다.
- 객체 이름, 질문, 명령, 배치에 개인정보·기밀·민감정보를 입력하지 않는다.
- AI 호출은 배치·요청·최근 대화 등 문맥을 Google에 전송한다.
- 무료 Gemini 입력/응답은 제품 개선에 사용되거나 사람이 검토할 수 있다.
  지역별 예외와 최신 조건은 [Gemini API 약관](https://ai.google.dev/gemini-api/terms)을 따른다.
- 키·프롬프트·제공자 오류 본문을 로그에 남기지 않으며, 조사 로그 공유 시에도 비밀/개인 식별자를 제외한다.
- 공용 AI 한도는 인증·방문자별 제한·전체 CPU 작업 보호를 대신하지 않는다. 악성 트래픽 대응은 운영자가 별도로 마련해야 한다.

## 7. 재시작과 영속 데이터

코드/runtime은 교체·재생성 가능하지만 상태는 반드시 **`/home/layout-data/`**에 둔다.

| 데이터 | 위치 / 수명 | 재시작·재배포 결과 |
|---|---|---|
| 명시적으로 저장한 배치 | `/home/layout-data/saved_layout.json` | 볼륨이 유지되면 다시 읽음 |
| AI 사용량/lock | `/home/layout-data/ai-quota.json`, `.lock` | 최근 호출 시각이 유지되어 한도 리셋 방지 |
| 원본 데모/지식 | runtime의 `backend/data` | 패키지 버전 사용. 사용자 저장으로 원본을 덮어쓰지 않음 |
| 저장하지 않은 편집 | 서버 메모리 | 사라짐. 저장본이 없으면 원본 데모로 시작 |
| Undo/Redo, 이력, 보류 명령 토큰 | 서버 메모리 | 사라짐 |
| 설명 캐시 | 서버 메모리 | 사라짐. 이후 재요청은 다시 차감될 수 있음 |
| 챗봇 대화 | 현재 브라우저 페이지 메모리 | 서버 영속 저장 대상 아님. 새로고침 시 초기화 |

**실제 코드 재배포와 재시작 전후에 저장본/사용량 파일의 SHA-256이 각각 정확히 동일함을 확인했고,
저장된 100점 배치가 자동 로드됨을 확인했다.** 이는 그 비교 구간의 증거이며 이후 정상 AI 호출은 사용량 파일을 변경한다.
건강 검사는 Gemini를 호출하지 않고 설정·사용량 파일·저장 폴더를 검사한다. 건강 검사 200만으로 실제 모델 동작을 보장하지 않는다.

## 8. 최종 패키징과 수동 재배포

### 8.1 커밋된 전용 스크립트 사용

긴 수동 pip/ZIP 조합이나 개별 의존성 파일의 직접 배포 대신 **`scripts/package_azure.py`**를 사용한다.

- 내부적으로 `git archive HEAD backend frontend requirements.txt`의 허용 목록을 사용한다.
- **커밋된 소스만** 포함하므로, 배포할 코드 변경은 검토/테스트/승인 후 먼저 커밋해야 한다.
- Linux CPython 3.12, `manylinux2014_x86_64`, `cp312`, binary-only wheel을 준비한다. 호스트 가상환경을 통째로 복사하지 않는다.
- ZIP 루트는 **`app.tar.gz`와 LF 형식 `start_azure.sh` 두 파일뿐**이다.
- 실제 생성물 **25.65 MB** 및 `.env`/저장본/사용량 데이터 미포함을 확인했다. 크기는 향후 의존성에 따라 달라질 수 있다.
- Git의 소유권 예외는 정확한 저장소 경로를 **각 명령의 `-c safe.directory=...`**에만 전달한다. 전역 설정을 변경하지 않는다.
- WSL Windows 체크아웃에서도 기본 Linux Git을 사용한다. `git.exe`나 별도 `--git` 인자가 필요하지 않다.

PowerShell, 저장소 루트에서(Python/pip/Git/Azure CLI가 준비된 환경):

```powershell
git branch --show-current
git status --short
git log -1 --oneline

# 추적 파일에 .env, 사용자 저장본, 키/토큰 파일이 없어야 한다.
git ls-files -- backend frontend requirements.txt scripts

python .\scripts\package_azure.py --output .\azure-runtime.zip
if ($LASTEXITCODE -ne 0) { throw "패키징 실패" }
```

WSL 사용자는 저장소 디렉터리에서 같은 스크립트를 기존 Linux Python 가상환경으로 실행한다.
생성 ZIP은 Git에 추가하지 않는다. 패키징은 실제 기동 검증을 대신하지 않으며 의존성 업데이트 후에도 아래 점검을 수행한다.

### 8.2 기존 앱 설정 적용 — 키는 출력/변경하지 않음

Azure CLI 로그인 및 의도한 학생 구독 선택은 운영자가 비공개로 확인한다. 아래 명령은 **기존 승인 자원**만 대상으로 한다.
`GEMINI_API_KEY`는 포털에서 등록한 값을 그대로 유지한다.

```powershell
az webapp config appsettings set --resource-group rg-wanted-layout-demo --name wanted-layout-kibum0613 --settings APP_ENV=production LLM_PROVIDER=gemini-free GEMINI_MODEL=gemini-3.5-flash-lite GEMINI_FREE_TIER_ONLY=true AI_QUOTA_FILE=/home/layout-data/ai-quota.json SAVED_LAYOUT_PATH=/home/layout-data/saved_layout.json WEBSITES_ENABLE_APP_SERVICE_STORAGE=true SCM_DO_BUILD_DURING_DEPLOYMENT=false ENABLE_ORYX_BUILD=false --output none
if ($LASTEXITCODE -ne 0) { throw "앱 설정 적용 실패" }

# 이전 직접 wheel 배포용 고정 경로는 제거한다. 시작 스크립트가 runtime 경로를 설정한다.
az webapp config appsettings delete --resource-group rg-wanted-layout-demo --name wanted-layout-kibum0613 --setting-names PYTHONPATH --output none
if ($LASTEXITCODE -ne 0) { throw "이전 PYTHONPATH 설정 정리 실패" }

az webapp config set --resource-group rg-wanted-layout-demo --name wanted-layout-kibum0613 --startup-file "sh /home/site/wwwroot/start_azure.sh" --output none
if ($LASTEXITCODE -ne 0) { throw "시작 명령 적용 실패" }
```

설정 변경/배포/재시작은 저장하지 않은 공용 작업을 잃게 할 수 있으므로 먼저 사용자 작업 유무를 확인한다.

### 8.3 현대식 배포 명령과 상태 확인

```powershell
az webapp deploy --resource-group rg-wanted-layout-demo --name wanted-layout-kibum0613 --src-path .\azure-runtime.zip --type zip --async true --clean true --output none
if ($LASTEXITCODE -ne 0) { throw "배포 요청 실패: 기존 배포 상태부터 확인하세요." }

az webapp log deployment list --resource-group rg-wanted-layout-demo --name wanted-layout-kibum0613 --query "[].{status:status,message:message}" --output table

# 비동기 요청 접수와 실제 기동 성공은 다르다. 해당 배포 완료/RuntimeSuccessful 확인 후:
Invoke-RestMethod -Uri "https://wanted-layout-kibum0613.azurewebsites.net/api/health?lang=en"
Invoke-RestMethod -Uri "https://wanted-layout-kibum0613.azurewebsites.net/api/inspect?lang=en"

# 배포와 점검이 끝난 뒤 로컬 생성물 정리
Remove-Item -LiteralPath .\azure-runtime.zip
```

`--clean true`는 이전 배포 코드 파일을 정리하므로 상태를 코드 폴더 안에 두지 않는다.
현재 성공 경로는 compact 패키지를 사용하는 현대식 `az webapp deploy`이다.
원격 Oryx가 다시 실행되지 않는지 두 플래그의 적용과 실제 배포 로그를 함께 확인한다.
시간 초과/게이트웨이 오류가 나면 바로 중복 배포하지 말고 기존 작업의 상태/로그/프로세스를 확인한다.

### 8.4 배포 후 검증

1. 건강 검사 200, 홈 HTML/정적 파일, 브라우저 3D 및 언어/개인정보 안내.
2. 현재 저장본/다른 사용자 작업을 확인한 뒤 승인된 통제된 씬에서 검사/자동 수정.
3. save/reset/restore/undo/redo 및 저장본·사용량 유지. 무단 재시작/초기화하지 않는다.
4. 민감정보 없는 실제 AI 설명/채팅/명령. 응답 문장뿐 아니라 `ops`, `applied`, 실제 씬 변경을 확인한다.
5. 429 동시성/할당량, 422 입력 거부가 정상이며 거부된 입력이 제공자를 호출하지 않는지 확인한다.
6. 배포 커밋·검증 결과·남은 제한을 이 문서에 반영한다. 한국어와 영어 성공을 서로 대신하는 증거로 사용하지 않는다.

**한국어 CLI 시험 주의:** Windows PowerShell 5의 기본 `$OutputEncoding`은 `us-ascii`다.
한글 리터럴을 포함한 here-string을 WSL Python에 파이프로 넘기면 HTTP 전송 전에 물음표로 손상될 수 있다.
UTF-8 파이프를 명시하거나 Python 소스에서 ASCII-only Unicode escape를 사용하고,
실제 전송 변수의 `ascii(text)`/예상 Unicode 비교로 입력 보존을 먼저 확인한다. 잘못된 입력의 결과를 모델 언어 능력 문제로 판정하지 않는다.

## 9. 장애 조사와 최종 우회가 아닌 대체 배포 방식

1. 최초 `az webapp deploy`의 게이트웨이 **502** 뒤에도 서버 측 작업은 `status=1 / Building`이었다.
   `az webapp log deployment list/show`와 인증된 `az rest` 상세 로그를 확인했다. 토큰/인증 헤더는 공개하지 않았다.
2. Oryx의 **Python 3.12.13 SDK tarball 추출**이 정체됐다. 제한된 시간 대기 후 원격 `ps`에서 Kudu 재시작과 남은 Oryx 프로세스 부재를 확인했다.
   계속 실행 중인 작업을 무작정 재배포하지 않았고 로컬 상태 조회 대기만 종료했다.
3. 개별 wheel 파일 ZIP을 준비해 `SCM_DO_BUILD_DURING_DEPLOYMENT=false`를 설정했지만 상속된 `ENABLE_ORYX_BUILD=true` 때문에 Oryx가 실행됐다.
4. 두 플래그를 모두 `false`로 명시/저장 확인하고 재시작했다. `az webapp deployment source config-zip`으로 기본 배포 스크립트와 `rsync` 복사를 확인했다.
   이 명령은 **CLI 2.90에서 deprecated**지만 조사 중 사용 가능했던 fallback이었다. 현재 재배포 권장 명령은 아니다.
5. 기본 파일 복사도 정체됐고 남은 `rsync` 프로세스가 없으며 사이트/Kudu 재시작이 관찰됐다.
   **정확한 원인은 확정하지 않았으며 OOM/메모리 부족이라고 단정하지 않는다.**
6. 수천 개 파일을 공유 볼륨에 직접 배포/import하는 대신, 단일 압축 payload를 배포하고 로컬 runtime에서 풀어 실행하도록 변경했다.
   원격 Python SDK 설치 없이 코드/의존성을 준비하는 방식이며 플랫폼 정책/권한을 우회한 것이 아니다.
7. 패키징을 끝까지 검증한 후 현대식 배포 명령으로 성공했다. 단순히 HTTP 오류를 숨기거나 임시 `http.server`를 성공으로 보고하지 않았다.

AI 조사 역시 구분한다. 최초 설명 오류의 원래 응답은 확보하지 못했고, 별도 동일 공개 데모 진단은 `STOP`, 정상 JSON,
출력 247/총 1,289 tokens였다. 출력 예산 부족으로 단정하지 않고 4,096 tokens를 유지하며 구조화 출력 계약을 추가했다.
수정 후 실제 설명 성공은 확인했다. **최초 설명 502는 한국어 요청 파이프와 무관한 실제 오류**이며 구조화 응답 수정의 검증은 유효하다.
반면 한국어 명령으로 의도한 이전 CLI 시험은 PowerShell 5 → WSL의 ASCII 파이프가 입력을 손상시킨 **시험 하네스 문제**였다.
이를 모델의 한국어 이름 해석 문제로 해석했던 결론은 철회한다. 이름 문맥 추가 자체는 명확성/사용자 지정 이름 지원에 유효한 독립적 개선이다.
하네스 입력을 바로잡은 재시험에서 실제 한국어 삭제가 성공했다.
따라서 “모델이 한국어를 이해하지 못했다가 수정 후 이해하게 됐다”는 결론을 내리지 않는다.

## 10. 검증 결과 — 무엇이 실제로 확인되었는가

| 항목 | 결과 |
|---|---|
| 최초 배포 준비 회귀 | 기존 80개 포함 **142 tests passed** |
| 구조화 출력 수정 후 전체 pytest | **153 passed**, 기존 deprecation 경고 2개, **13.11초** |
| Node 테스트 환경 | WSL Windows `.exe` 실행 형식 오류 후 checksum 검증한 격리 Linux Node.js 24.18 사용. 프로젝트 의존성 추가 없음 |
| 이름 문맥 보완 후 관련 테스트 | **114 passed**. 전체 153개 검증과 별도 시점/범위이며 실제 한국어 성공 증거가 아님 |
| 최종 전체 pytest | **159 passed**, 기존 deprecation 경고 2개, **13.57초**, **skip 없음** |
| compact 패키지 | **25.65 MB**, `app.tar.gz` + LF `start_azure.sh`만 포함, 비밀/저장본/사용량 미포함 |
| 현대식 배포 결과 | **RuntimeSuccessful**, 성공 인스턴스 1/실패 0. 앞선 후속 배포 빌드 1초·기동 81초, 최종 `3454627` 배포 78초 |
| 실제 건강 검사 | **200**, `gemini-free`, 10 RPM/400 rolling 24h/동시 1 |
| 실제 자동 수정 | 초기 9건·0점 → **5 actions, 0건·100점**. 네트워크 포함 앞선 **3.567초/4.301초**, 최종 **4.289초** |
| 실제 저장/초기화/복원/Undo/Redo | 통과 |
| 재배포·재시작 영속성 | 저장본/사용량 SHA-256 각각 정확히 동일, 저장 100점 배치 자동 로드 |
| 실제 Gemini 설명 | 수정 후 **성공**, 3.23초, `llm=true`, 필수 JSON 형태 정상 |
| 실제 영어 채팅 | 성공 |
| 명시적 영어 ID 삭제 | **실제 소파 삭제 성공**, `ops: [{"op":"delete","id":"sofa"}]`, 실제 씬에서 부재 확인 |
| 이전 한국어 CLI 삭제 시험 | **무효** — HTTP 전 ASCII 파이프에서 입력 손상 확인. 모델/서비스 한국어 제한의 근거가 아님 |
| Unicode 보존 한국어 삭제 | **성공**, 실제 소파 부재 확인. 명령 + 후속 씬 조회 **3.221초**, `3454627` |
| 실제 동시 채팅 2개 | **하나 200, 하나 429 `ai_busy`, Retry-After 5** |
| 501자 채팅 | **422**, 제공자 호출 없이 거부 |
| 공개 브라우저 | UI/3D canvas, 한국어/영어 및 개인정보 안내 전환 확인. 검증한 공유 뷰포트에서 가로 넘침 없음 |
| 공개 브라우저 한국어 명령 end-to-end | 실제 Unicode 입력/실행 후 소파 사이드바 항목이 사라지고 WebGL canvas가 유지됨. Demo Reset 후 소파와 기본 배치 복귀 |
| 검증 후 상태 | 작업 화면은 **기본 9건**으로 초기화, **저장된 100점 배치는 유지** |

모든 화면 크기/브라우저, 계정별 할당량, 미래 의존성 버전까지 검증했다는 뜻은 아니다.

### 최종 한국어 실제 요청 증거

ASCII 파이프 손상을 피하도록 시험 코드에서 입력을 Unicode escape로 만들고 실제 전송 값이 의도한 문자열인지 확인했다.

```python
text = "\uc18c\ud30c\ub97c \uc0ad\uc81c\ud574 \uc918"
```

실제 요청 텍스트: **소파를 삭제해 줘**

응답의 관련 필드:

```json
{
  "reply": "요청하신 소파를 삭제했습니다.",
  "applied": ["소파 (거실) 삭제"],
  "ops": [{"op": "delete", "id": "sofa"}]
}
```

응답 문장만 확인한 것이 아니라 후속 `/api/scene`에서 `sofa`가 없는 것을 확인했다.
이후 원본 초기화 → 자동 수정 5회·0건·100점을 확인하고 다시 기본 9건 작업 화면으로 초기화했다.
별도의 100점 저장본은 유지했다.

HTTP 시험뿐 아니라 공개 브라우저에서도 한국어를 선택하고 실제 Unicode 문장을 입력해 실행했다.
소파 사이드바 항목이 사라졌고 WebGL canvas는 계속 보였으며, **Demo Reset**을 누르자 소파와 기본 배치가 돌아왔다.

## 11. 남은 운영자 책임

- 한국어 시험은 실제 Unicode 입력 보존부터 확인하고 작업 반영을 검증한다. 깨진 파이프 입력이나 영어 성공으로 대신하지 않는다.
- 비용 추세, spending limit, 크레딧 만료일, 남아 있는 과금 자원을 주기적으로 확인한다.
- Google 프로젝트가 무료/결제 미연결인지, 모델/계정 할당량이 유지되는지 확인한다.
- 키 권한을 제한하고 유출 의심 시 회전한다. 공개 로그/문서/Git에 키를 남기지 않는다.
- 인스턴스/worker를 1개로 유지한다. 확장 전에는 공유 상태·전역 한도 설계를 먼저 변경해야 한다.
- 사용량 파일을 삭제/롤백해 한도를 우회하지 않으며 손상 시 보수적으로 복구한다.
- 개인정보 안내, 인증 없는 공용 씬이라는 제한, 트래픽 방어 필요성을 유지한다.
- 외부 Three.js CDN, 런타임/의존성 업데이트 후 기능 변화를 확인한다. 현재 requirements의 버전 고정 여부도 운영 중 관리한다.
- 데모 종료 시 앱 중지만으로 과금이 멈춘다고 오해하지 않고 백업/승인 후 전용 플랜·자원을 정리한다.

참고: [Azure Python App Service 구성](https://learn.microsoft.com/azure/app-service/configure-language-python),
[ZIP 배포](https://learn.microsoft.com/azure/app-service/deploy-zip),
[플랜 관리](https://learn.microsoft.com/azure/app-service/app-service-plan-manage),
[Linux App Service 가격](https://azure.microsoft.com/pricing/details/app-service/linux/),
[Gemini API 약관](https://ai.google.dev/gemini-api/terms).
