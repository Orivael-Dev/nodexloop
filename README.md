# NodeXLoop

**Debug AI agents like you debug code.**

[![VS Code Marketplace](https://img.shields.io/visual-studio-marketplace/v/orivael.loop-graph-engineer?label=VS%20Code%20Marketplace&color=0E8FA8)](https://marketplace.visualstudio.com/items?itemName=orivael.loop-graph-engineer)
[![Open VSX](https://img.shields.io/open-vsx/v/orivael/loop-graph-engineer?label=Open%20VSX&color=0E8FA8)](https://open-vsx.org/extension/orivael/loop-graph-engineer)
[![License](https://img.shields.io/badge/license-Apache--2.0-green)](LICENSE)

NodeXLoop is a visual engineering environment for building, running and
governing AI agent loops — agent → tool → critic → retry → gate → code
change → test → approve — with live model calls, breakpoints, runtime
permissions and run replay. It ships as a VS Code extension, with the same
app runnable in the browser.

Every prompt and completion passes an embedded **Axiom guard** before it
moves. The guard is on by default and correct with no network: its pattern
banks are generated from the same engine behind Orivael's intent firewall
and verified against it by a parity corpus. When a critic loop stalls, the
loop governor stops it instead of letting it burn model calls.

## Install

| Channel | How |
|---|---|
| **VS Code Marketplace** | [NodeXLoop](https://marketplace.visualstudio.com/items?itemName=orivael.loop-graph-engineer) — or search "NodeXLoop" in the Extensions view |
| **Open VSX** (VSCodium, Cursor, Gitpod) | [orivael/loop-graph-engineer](https://open-vsx.org/extension/orivael/loop-graph-engineer) |
| **Direct `.vsix`** | [Releases](https://github.com/Orivael-Dev/nodexloop/releases/latest) — then VS Code → Extensions → `···` → *Install from VSIX*. Each release lists its SHA-256. |
| **Browser, no install** | [nodexloop.orivael.dev](https://nodexloop.orivael.dev) — sim mode runs whole loops offline, no account, no API key |

Live runs work with your own OpenAI / Anthropic / Google / OpenRouter key,
or keyless against a local [Ollama](https://ollama.com). Sim mode needs
nothing at all.

## Read more

**[NodeXLoop_Product_Overview.pdf](NodeXLoop_Product_Overview.pdf)** — the
11-page product overview: the idea, the debugger and the governor, the
loop library, how the RL-style loops avoid reward hacking with held-out
judges, and a straight-talk page on current limits.

## The Template Demo Book

**[NODEXLOOP_TEMPLATE_DEMOS.pdf](NODEXLOOP_TEMPLATE_DEMOS.pdf)** — a demo
of every built-in template: all 29, across five groups (build · debug your
company · debug your life · enterprise · meta).

Nothing in it is typed in. Each page shows the template's real graph drawn
from its canvas coordinates, a full offline run trace, and a
guard-OFF-vs-ON model-call comparison — all produced by an actual seeded,
networkless run of the app: seeded RNG, network disabled, and no model or
API key involved anywhere.

## Measured, honestly

From the integration harness (stubbed model, real app, real guard):

| Scenario | Guard OFF | Guard ON |
|---|---|---|
| Critic loop that stops improving | 20 model calls | **6** |
| Prompt injection in the input | runs normally | **0 calls** |
| Loop that is genuinely improving | 12 | 12 — no penalty |

The demo book adds per-template numbers (repo-regression bisector 27 → 9,
drift-and-oscillation 24 → 6, context-degradation stress test 21 → 7,
self-healing CI 14 → 8) — and reports the two templates where the guard's
preflight false-positives on the template's own adversarial persona,
because a measurement you only publish when it flatters you isn't a
measurement.

## Experimental builds

Pre-release `.vsix` builds land here as GitHub
[**pre-releases**](https://github.com/Orivael-Dev/nodexloop/releases).
Expect rough edges; the stable channel is the Marketplace / Open VSX
listing, which updates automatically.

## Privacy

The guard classifies in-process — prompts are not sent anywhere for
checking. In live mode your prompts go only to the model provider you
configured. Locally sealed run manifests are tamper-evident on your
machine; they do not claim more than that.

## License

[Apache-2.0](LICENSE).
