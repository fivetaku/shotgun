# Disclaimer & Acceptable Use — shotgun

`shotgun` is a standalone plugin by the author of
[gptaku-plugins](https://github.com/fivetaku/gptaku_plugins) and is distributed
under the [MIT License](./LICENSE).
Copyright (c) 2026 fivetaku.

This document does not modify the MIT License; it clarifies the author's intent
and the responsibilities of anyone who uses, integrates, or redistributes this
software. Where this document and the LICENSE appear to differ, the LICENSE
governs the legal grant and the disclaimer of warranty and liability.

## 1. No warranty

The software is provided **"AS IS"**, without warranty of any kind, express or
implied, including but not limited to the warranties of merchantability, fitness
for a particular purpose, and non-infringement. The author does not guarantee
that the software is correct, complete, reliable, secure, available, or suitable
for any particular purpose, and does not guarantee any specific result from its
use.

## 2. Limitation of liability

In no event shall the author or copyright holder be liable for any claim,
damages, loss, or other liability — whether in an action of contract, tort
(including negligence), or otherwise — arising from, out of, or in connection
with the software or the use of or other dealings in the software. You use the
software entirely at your own risk.

## 3. Microphone use and privacy

`shotgun` opens your microphone **locally, on your machine, only while a
Claude Code session is alive**, in order to measure sound volume levels. Audio
is reduced to per-block loudness numbers (RMS) in memory. **No audio is
recorded, stored on disk, or transmitted anywhere — ever.** What is written to
disk is a small text line per detection (timestamp and loudness number). You
are responsible for complying with any laws, workplace policies, or third-party
rights that apply to operating a microphone in your environment (for example,
in shared spaces where others may be audible).

## 4. Intended use and dual-use nature

`shotgun` is a general-purpose developer tool. Like most general-purpose tools,
it is inherently dual-use: it is published for legitimate, lawful, and
authorized purposes, and the author has no ability to monitor, approve, or
control how third parties actually use it.

## 5. No affiliation or endorsement

The author is **not affiliated with**, and does **not** endorse, sponsor,
support, or take responsibility for, any third-party project that derives from,
integrates, forks, embeds, redistributes, or otherwise builds upon this
software. The MIT License permits such downstream use without the author's
review or approval. The existence of any downstream project does **not** imply
any relationship with, contribution by, or approval from the author, and any
responsibility or liability for such a project rests entirely with its own
authors and users.

## 6. Your responsibility

You are solely responsible for how you use this software, including full
compliance with all applicable laws and regulations and with the terms of
service of any system, network, platform, or website you interact with through
it. Misuse — including any unlawful or unauthorized activity — is solely your
responsibility. Also: please don't actually break your desk, your keyboard, or
your hand. The plugin only needs the sound.
