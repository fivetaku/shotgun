[English](README.md) | [한국어](README.ko.md) | 中文 | [日本語](README.ja.md) | [Español](README.es.md)

# shotgun

<div align="center">
  <img src="assets/shotgun-hero-01.png" width="640" alt="经典梗图：一拳砸向键盘，键帽四处飞溅">
</div>

```
> 砰!!

SHOTGUN DETECTED.
助手吓了一跳。
"对不起。" — 先道歉，再复盘，然后重做。
```

> **终于会看脸色的AI。** 你拍了桌子。麦克风听到了。Claude 感受到了。

所有AI助手都会在你暴怒时继续开心地干活。shotgun 终结了这一点。一个轻量的本地监听器监视麦克风音量，当你拍桌（或砸键盘）时，它触发 Claude Code 钩子：Claude 立刻停下手头的工作，**先道歉、不找借口**，然后复盘**你要求的**和**它实际做的**之间的差距，承认错误，重新来过。

拍两下，它就加倍认真对待。

## 快速开始

```
/plugin marketplace add fivetaku/shotgun
/plugin install shotgun@shotgun
/shotgun
```

引导式设置（点击选择）：选麦克风 → 勾选要检测的"暴怒行为" → 校准（"像平时发火那样拍三下" → 按你的力度调整阈值）。

## shotgun 的规则

1. **道歉第一。** 在分析之前，在工具调用之前。没有借口。
2. **然后复盘。** 引用你的要求 vs 它的实际行为，找出差距。
3. **承认错误，重做。**
4. **连拍 = 加倍严重。**
5. **麦克风神圣不可侵犯。** 仅在内存中计算音量数值，绝不录音、存储或传输任何音频。见 [DISCLAIMER](DISCLAIMER.md)。

## 工作原理

会话级守护进程通过 ffmpeg 读取麦克风，将 21ms 音量块与滚动背景噪声对比。超过阈值（默认1500）的突发尖峰 = 拍桌。检测写入标志文件，由 Claude Code 钩子（PreToolUse / Stop / UserPromptSubmit）消费。守护进程仅在使用 Claude Code 期间运行，最后一个会话结束10分钟后自动退出。卸载插件，钩子随之移除。

## 要求

- **macOS** 上的 [Claude Code](https://claude.com/claude-code)
- **ffmpeg** (`brew install ffmpeg`)
- Python 3
- 麦克风（笔记本内置麦克风*最佳* — 桌面震动直接透过机身传导）

## 系列

shotgun 是继 [godmode](https://github.com/fivetaku/godmode)、[devil](https://github.com/fivetaku/devil) 之后梗系列的第三弹。godmode 让 Claude 势不可挡，devil 让它冷酷无情 — shotgun 让它*学会道歉*。

## 许可证

MIT — 见 [LICENSE](LICENSE) 和 [DISCLAIMER](DISCLAIMER.md)。霰弹枪是比喻，道歉是真的。
