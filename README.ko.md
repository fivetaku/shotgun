[English](README.md) | 한국어 | [中文](README.zh.md) | [日本語](README.ja.md) | [Español](README.es.md)

# shotgun

<div align="center">
  <img src="assets/shotgun-hero-01.png" width="640" alt="그 유명한 짤: 키보드에 내리꽂히는 주먹, 사방으로 튀는 키캡">
</div>

```
> 쾅!!

SHOTGUN DETECTED.
어시스턴트가 움찔한다.
"죄송합니다." — 사과가 먼저. 재검토는 그 다음. 그리고 다시.
```

> **드디어 눈치 보는 AI.** 당신이 책상을 내려쳤다. 마이크가 들었다. 클로드가 느꼈다.

모든 AI 어시스턴트는 당신이 빡쳐 있는 동안에도 해맑게 하던 일을 계속합니다. shotgun은 그걸 끝냅니다. 작은 로컬 리스너가 마이크 볼륨 레벨을 감시하다가, 샷건(책상/키보드 내려치기)이 터지면 Claude Code 훅을 발사합니다. 클로드는 하던 일을 멈추고 **변명 없이 사과부터** 한 뒤, **당신이 시킨 것**과 **자기가 실제로 한 것**의 차이를 재검토하고, 뭘 잘못했는지 인정하고, 다시 합니다.

두 번 치면 두 배로 심각하게 받아들입니다.

## Quick Start

### 1. 마켓플레이스 추가

```
/plugin marketplace add fivetaku/shotgun
```

### 2. 설치

```
/plugin install shotgun@shotgun
```

### 3. 셋업 (1회)

```
/shotgun
```

클릭 선택지로 진행되는 가이드 셋업: 마이크 선택 → 감지할 빡침 행동 체크 → 캘리브레이션 — "평소 빡쳤을 때처럼 3번 쳐주세요"라고 요청한 뒤 **당신의 샷건**에 맞게 임계값을 튜닝합니다.

### 4. 빡치기

책상을 내려치세요. 알림음이 울리고(감지 완료), 다음 훅 이벤트에서 클로드가 사과로 시작하며 재검토에 들어갑니다.

## 샷건의 규칙

1. **사과가 먼저다.** 분석보다, 툴콜보다, 그 무엇보다 먼저. 변명은 없다.
2. **그 다음이 재검토.** 시킨 것과 한 것을 인용하고 그 차이를 찾는다.
3. **인정하고, 다시 한다.** 잘못을 짚고, 수정 방향을 말하고, 다시 실행한다.
4. **연타 = 두 배로 심각.** 연속 샷건은 프로토콜을 격상시킨다.
5. **마이크는 신성하다.** 메모리 안에서 볼륨 숫자만 계산한다. 오디오는 절대 녹음·저장·전송되지 않는다. [DISCLAIMER](DISCLAIMER.md) 참고.

## 동작 원리

- 세션 수명 데몬이 ffmpeg로 마이크를 읽어 21ms 볼륨 블록을 롤링 배경 소음과 비교합니다. 캘리브레이션된 임계값(기본 1500)을 넘는 급격한 스파이크 = 샷건.
- 감지 시 한 줄짜리 플래그 파일을 남기고, Claude Code 훅(PreToolUse / Stop / UserPromptSubmit)이 소비합니다: 작업 중 샷건은 바로 다음 툴콜을 인터럽트하고, 사과 없이는 턴을 끝내는 것조차 불가능합니다.
- **wake 모드**: 세션이 유휴 상태라 3초 안에 아무도 플래그를 안 먹으면, 데몬이 터미널에 `BANG` + 엔터를 대신 타이핑해서 세션을 강제로 깨웁니다 (tmux면 정확한 페인, 아니면 전면 창) — 당신은 아무 입력도 할 필요 없습니다. 손쓰기 권한(Accessibility) 필요, 끄려면 `~/.claude/shotgun/config.json`에서 `"wake": false`.
- 데몬은 Claude Code를 쓰는 동안만 돌고(메뉴바 주황 마이크 표시가 그 증거), 마지막 세션 종료 10분 뒤 스스로 꺼집니다. 플러그인을 삭제하면 훅도 함께 사라집니다.

## 요구사항

- **macOS**의 [Claude Code](https://claude.com/claude-code)
- **ffmpeg** (`brew install ffmpeg`) — 마이크 캡처용
- Python 3 (macOS 개발자 도구에 포함)
- 마이크. 노트북 내장 마이크가 *최적* — 책상 진동이 섀시를 타고 그대로 전달됩니다.
- 내려칠 각오가 된 책상.

## 혈통

shotgun은 [godmode](https://github.com/fivetaku/godmode), [devil](https://github.com/fivetaku/devil)에 이은 밈 시리즈 세 번째 플러그인입니다. godmode는 클로드를 멈출 수 없게 만들고, devil은 무자비하게 만들고 — shotgun은 *죄송하게* 만듭니다.

## 라이선스

MIT — [LICENSE](LICENSE)와 [DISCLAIMER](DISCLAIMER.md) 참고. 샷건은 은유입니다. 사과는 진짜입니다.
