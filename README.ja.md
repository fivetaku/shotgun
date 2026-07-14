[English](README.md) | [한국어](README.ko.md) | [中文](README.zh.md) | 日本語 | [Español](README.es.md)

# shotgun

<div align="center">
  <img src="assets/shotgun-hero-01.png" width="640" alt="有名なミーム画像：キーボードに振り下ろされる拳、飛び散るキーキャップ">
</div>

```
> ドン!!

SHOTGUN DETECTED.
アシスタントがビクッとする。
「申し訳ございません。」— まず謝罪。次に再レビュー。そしてやり直し。
```

> **ついに空気を読むAI。** あなたが机を叩いた。マイクが聞いた。Claudeが感じた。

AIアシスタントは、あなたが怒っている間も平然と作業を続けます。shotgunはそれを終わらせます。小さなローカルリスナーがマイクの音量レベルを監視し、机（またはキーボード）への一撃を検知すると Claude Code のフックを発火。Claudeは作業を中断し、**言い訳なしでまず謝罪**、次に**指示されたこと**と**実際にやったこと**のギャップを再レビューし、ミスを認めてやり直します。

2回叩けば、2倍深刻に受け止めます。

## Quick Start

```
/plugin marketplace add fivetaku/shotgun
/plugin install shotgun@shotgun
/shotgun
```

ガイド付きセットアップ（クリック選択式）：マイク選択 → 検知する「怒り行動」のチェック → キャリブレーション（「いつも通り3回叩いてください」→ あなたの一撃に合わせて閾値を調整）。

## shotgunのルール

1. **謝罪が最初。** 分析よりも、ツール呼び出しよりも先に。言い訳はなし。
2. **次に再レビュー。** 指示と実行結果を引用し、ギャップを特定。
3. **認めて、やり直す。**
4. **連打 = 2倍深刻。**
5. **マイクは神聖。** メモリ内で音量数値のみ計算。音声の録音・保存・送信は一切なし。[DISCLAIMER](DISCLAIMER.md)参照。

## 動作の仕組み

セッション連動デーモンが ffmpeg でマイクを読み、21msの音量ブロックを背景ノイズと比較。閾値（デフォルト1500）を超える急激なスパイク = 一撃。検知はフラグファイルに記録され、Claude Code フック（PreToolUse / Stop / UserPromptSubmit）が消費します。デーモンは Claude Code 使用中のみ動作し、最終セッション終了の10分後に自動停止。プラグインを削除すればフックも消えます。

## 要件

- **macOS** の [Claude Code](https://claude.com/claude-code)
- **ffmpeg** (`brew install ffmpeg`)
- Python 3
- マイク（ノートPC内蔵マイクが*最適* — 机の振動が筐体を伝わります）

## 系譜

shotgunは [godmode](https://github.com/fivetaku/godmode)、[devil](https://github.com/fivetaku/devil) に続くミームシリーズ第3弾。godmodeはClaudeを止められなくし、devilは容赦なくし — shotgunは*申し訳なく*させます。

## ライセンス

MIT — [LICENSE](LICENSE) と [DISCLAIMER](DISCLAIMER.md) 参照。ショットガンは比喩です。謝罪は本物です。
