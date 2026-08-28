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

## New in 3.6.0

**Organizations.** Submit a graph, have a person read it, and only then can
anyone load it — `submit → sandbox → approved → released`, with every
transition recording who made it. Most first agent loops are bad ones, and the
fix that scales is a colleague's graph with the parts that make it work still
attached.

> **Local preview.** Org data lives in your browser: no server, no account, and
> an invite code resolves for you and not for a colleague on another machine.
> The review pipeline and the stats are real; the cross-device sharing is not
> yet. The app says so on the sign-in card, in the signed-in view, and when a
> code is refused.

**Save-this-loop suggestion.** Run the same loop shape three times and it
offers to save it as a template, or submit it to your org. The signature is the
node types and edge count, not the prompts — so it matches a pattern you are
reusing even when every prompt differs.

**A Help tab.** Three steps to a first run, plus the things that are not
obvious from the canvas: Sim mode spends nothing *and never invokes the guard*,
the guard classifies before the call so a blocked node costs zero tokens, and
F9 is the breakpoint key because it is the one your editor already uses.

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
of every built-in template: all 35 at the time it was generated, across six
groups (build · debug your company · debug your life · enterprise · debug the
agent · govern the agent). 3.6.0 ships **37** — the two community templates
above were promoted after the book was last regenerated.

Nothing in it is typed in. Each page shows the template's real graph drawn
from its canvas coordinates, a full offline run trace, and a
guard-OFF-vs-ON model-call comparison — all produced by an actual seeded,
networkless run of the app: seeded RNG, network disabled, and no model or
API key involved anywhere.

## Community templates (experimental)

**[templates/](templates/)** — a **legal document drafter** and a **driver
update & hardening loop**.

**Both now ship inside the extension** as of 3.6.0, still marked experimental,
which also means they go through the built-in template suite they had never
been held to. The copies here stay importable for anyone on an older build:
`.loop.yaml` in the VS Code extension (`···` → *Import .loop.yaml*) or
`.graph.json` in the web app.

Experimental, and each carries a disclaimer that travels inside the graph. In
particular the legal drafter is **not a legal service and not legal advice** —
its output is an unreviewed AI draft, and you should always have any legal
document reviewed by a lawyer licensed in the relevant jurisdiction. The driver
loop is **review-only** and never installs anything. See
[templates/README.md](templates/README.md).

## Measured, honestly

From the integration harness (stubbed model, real app, real guard):

| Scenario | Guard OFF | Guard ON |
|---|---|---|
| Critic loop that stops improving | 20 model calls | **6** |
| Prompt injection in the input | runs normally | **0 calls** |
| Loop that is genuinely improving | 12 | 12 — no penalty |

The demo book adds per-template numbers (repo-regression bisector 27 → 9,
drift-and-oscillation 24 → 6, context-degradation stress test 21 → 7,
self-healing CI 14 → 8) — and shows the exemption that stops a template's
own sanctioned adversarial critic ('devil's advocate', 'risk judge') from
tripping the guard's HARM preflight, while a real attack and the data
flowing through the node still block. A measurement you only publish when
it flatters you isn't a measurement.

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
