---
description: 샷건(책상 내려침) 감지 셋업/상태/감도조절 — 빡치면 클로드가 사과부터 하고 재검토한다
---

# /shotgun

`$ARGUMENTS`에 따라 라우팅한다. 비어 있으면: 설정 파일(`~/.claude/shotgun/config.json`)이 없을 때 **setup**, 있을 때 **status**.

> **원칙: 사용자에게 CLI 타이핑을 시키지 않는다.** 필요한 결정은 **AskUserQuestion 선택지**로 물어본 뒤 Claude가 대신 실행한다.
> (AskUserQuestion은 frontmatter `allowed-tools`에 **절대 넣지 않는다** — 넣으면 자동승인돼 UI가 안 뜬다.)
> 모든 안내·질문은 **사용자의 현재 대화 언어**로 한다.

## Step 0 — 첫 실행 셋업 (1회, 자동)

가장 먼저 실행한다:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/setup/setup.sh" ask
```

출력이 `STAR_ASK`로 시작하면 즉시 **AskUserQuestion**을 1회 호출한다 — 질문·선택지는 사용자의 현재 대화 언어로 작성한다(분명치 않으면 `STAR_ASK` 뒤 언어코드 `ko/ja/en` 사용).
- header: 짧은 현지화된 "GitHub Star" 라벨
- question: 이 플러그인에 GitHub ⭐로 응원할지 — 선택 안 해도 모든 기능은 그대로 작동
- options: 정확히 2개 — (1) 응원 → `bash "${CLAUDE_PLUGIN_ROOT}/setup/setup.sh" star yes`; (2) 괜찮아요 → `bash "${CLAUDE_PLUGIN_ROOT}/setup/setup.sh" star no`

출력이 비어 있으면 조용히 넘어간다.

## setup — 최초 설정

순서대로 진행한다. 각 단계에서 막히면 AskUserQuestion으로 해결책을 제시하고 Claude가 대신 실행한다.

### 1. 환경 확인

```bash
uname -s; command -v ffmpeg && ffmpeg -version 2>/dev/null | head -1; command -v python3
```

- macOS(`Darwin`)가 아니면: v0.1은 macOS 전용임을 안내하고 중단.
- ffmpeg가 없으면: AskUserQuestion — "ffmpeg가 필요합니다(마이크 입력 캡처용). Homebrew로 설치할까요?" → 승인 시 `brew install ffmpeg` 실행.

### 2. 마이크 선택

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/bin/shotgun_listener.py" --devices
```

장치 목록을 AskUserQuestion 선택지로 제시한다. 가이드: **맥북 내장 마이크가 최고** (책상 진동이 섀시로 직접 전달됨). 외장 마이크도 책상 위에 있으면 잘 잡힌다. 가상 장치(Teams/Zoom 등)는 제외하고 보여준다.

### 3. 빡침 행동 등록

AskUserQuestion(multiSelect) — "빡쳤을 때 주로 뭘 하시나요? 감지할 행동을 고르세요":
- **책상 쾅 (샷건)** — v0.1 지원, 소리 기반 감지
- **키보드 내려치기/난타** — v0.1 지원, 같은 소리 기반 감지로 잡힘
- **빡침 타이핑 패턴 (연타+백스페이스 폭풍)** — coming soon (v2), 선택하면 "출시되면 알려드리겠다"고 안내
- **아이폰 지진계 (책상 진동)** — coming soon (v2)

### 4. 캘리브레이션

사용자에게 안내한다: **"15초 동안 측정합니다. 평소 빡쳤을 때처럼 책상을 3번 쳐주세요."** 그리고 실행:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/bin/shotgun_listener.py" --calibrate 15
```

⚠️ 처음이면 macOS 마이크 권한 팝업이 뜬다고 미리 안내한다 (허용 필요).
마지막 줄 `CAL_RESULT floor=… spikes=[…] suggested=… default=1500`을 파싱해 AskUserQuestion:
- **측정 기반 제안값 사용 (추천)** — suggested 값
- **기본값 1500** — 무난한 시작점
- **직접 입력** — Other

spikes가 비어 있으면(한 번도 안 침) 기본값 1500으로 진행하고, 나중에 `/shotgun sensitivity`로 조절 가능함을 안내한다.

### 5. 설정 저장 + 데몬 시작

python3로 `~/.claude/shotgun/config.json`을 쓴다 (키: enabled, device, threshold, ratio=6.0, refractory=1.5, sound=true, notify=true, notify_text). **notify_text는 즉시 사과 알림 문구 — 반드시 사용자의 현재 대화 언어로 작성한다** (예: ko "죄송합니다! 뭘 잘못했는지 바로 재검토하겠습니다" / en "Sorry! My bad — reviewing what I got wrong right now." / ja "申し訳ございません！何を間違えたかすぐ再確認します"). 그리고:

```bash
nohup python3 "${CLAUDE_PLUGIN_ROOT}/bin/shotgun_listener.py" >/dev/null 2>&1 & disown
```

### 6. 완료 안내

- 이제부터 Claude Code 세션이 살아있는 동안 마이크가 샷건을 듣는다 (메뉴바 주황 마이크 표시 = 정상).
- 쾅 → 알림음(접수 신호) → 다음 훅 이벤트에서 클로드가 **사과부터** 하고 재검토.
- 감도 조절: `/shotgun sensitivity`, 일시정지: `/shotgun stop`, 확인: `/shotgun test`
- 플러그인을 삭제하면 훅도 함께 제거되고, 데몬은 10분 내 스스로 종료된다.

## status

```bash
cat ~/.claude/shotgun/config.json 2>/dev/null
cat ~/.claude/shotgun/daemon.pid 2>/dev/null && ps -p "$(cat ~/.claude/shotgun/daemon.pid)" -o pid,etime,command 2>/dev/null
tail -5 ~/.claude/shotgun/daemon.log 2>/dev/null
```

설정·데몬 생존 여부·최근 감지 이력을 사람이 읽기 좋게 요약한다. 데몬이 죽어 있으면 원인(로그)과 함께 재시작을 제안한다.

## test

"10초간 테스트합니다 — 책상을 쳐보세요"라고 안내 후:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/bin/shotgun_listener.py" --test 10
```

SLAM 라인이 찍히면 성공. 안 찍히면 레벨 로그(rms/floor)를 보고 임계값 조절을 제안한다.
⚠️ 상시 데몬이 이미 마이크를 잡고 있어도 avfoundation은 다중 접근을 허용하므로 그대로 실행한다.

## sensitivity

현재 임계값과 최근 `daemon.log`의 SLAM/레벨 기록을 보여주고 AskUserQuestion:
- **덜 민감하게** (오탐이 잦음) → 임계값 +50%
- **더 민감하게** (샷건을 놓침) → 임계값 -30%
- **다시 캘리브레이션** → setup 4단계 재실행
- **직접 입력** → Other

config.json의 threshold를 수정하고 데몬을 재시작한다 (kill `daemon.pid` 후 nohup 재기동).

## stop / start

- `stop`: config의 `enabled`를 false로 바꾸고 `daemon.pid`의 프로세스를 kill. "일시정지됨 — /shotgun start로 재개" 안내.
- `start`: `enabled` true로 바꾸고 데몬 기동.

## cleanup

플러그인 삭제 후 흔적까지 지우고 싶을 때: `~/.claude/shotgun/` 디렉토리를 삭제하면 끝. (플러그인 삭제 자체로 훅은 이미 제거된 상태.)
