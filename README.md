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

## Features

### The canvas and the debugger
- **Visual agent-loop canvas** — agent → tool → critic → retry → gate → code
  change → test → approve, with ten node types, drag-and-drop wiring, undo,
  and graph import/export.
- **Breakpoints and stepping** — F9 on a node, execution pauses *before* it
  runs so you can read exactly what it was about to send; step, continue,
  stop from the debug bar.
- **Run replay and history** — every run is kept node-by-node and can be
  replayed; live runs stream into the Runs tab as they execute.
- **Sim mode** — whole loops run offline with synthetic outputs: no key, no
  account, zero model calls. Good for learning the shape before spending.

### Governed execution
- **Axiom guard, on by default** — every prompt and completion is classified
  in-process *before* it moves; a blocked node costs zero tokens and halts
  only its own branch. Pattern banks are generated from Orivael's intent
  firewall and held to a parity corpus against it. No network needed.
- **Loop governor** — a critic loop that stops improving is cut early instead
  of burning its remaining iterations; a loop still improving is untouched.
- **Prompt-injection preflight** with a persona exemption, so a template's
  own sanctioned adversarial critic doesn't trip the guard while a real
  attack still blocks.
- **Per-node runtime permissions** — recorded and audited on every run
  (enforcement is on the roadmap and the README says so rather than implying
  more).

### Module Resolver — governed capability loading *(3.7)*
- **"This loop needs pygame"** becomes a governed workflow: resolve on PyPI,
  a deterministic seven-check policy gate (typosquat distance, registry
  allowlist, pinned version, registry sha256, install-script warning,
  license), an isolated per-project or ephemeral environment, and a locally
  sealed receipt of the whole decision. No model anywhere in the path.
- **Version-correct API context** — the *installed* version's symbols,
  signatures and docstring heads are indexed so coding nodes stop guessing
  which APIs exist.
- **Module node on the canvas** *(3.7.1)* — drag it from the Capabilities
  palette, name a package, Resolve & install runs the governed flow, and at
  run time the node injects the API context downstream for zero tokens.

### Models
- **Model registry** — OpenAI, Anthropic, Google, OpenRouter, a local
  Ollama, or any OpenAI-compatible endpoint; per-node model choice,
  favourites, and a default. API keys live in the OS keychain in the
  extension.
- **Duplicate as custom** — point a built-in model at another endpoint (NIM,
  vLLM, a gateway) without losing its defaults. *(Fixed in 3.7.1 — the
  button silently did nothing since the built-in identity lock landed.)*
- **Cost estimates labelled as estimates** — with unpriced calls counted,
  never papered over.

### The editor edition (VS Code)
- **The graph is a file** — bidirectional sync with a `.loop.yaml` next to
  your code: edit the canvas or the file, either stays true, and the loop
  reviews in the same pull request as the code it drives.
- **CodeLens on bound functions** and a stale-binding warning in the
  Problems panel the moment a refactor breaks a binding.
- **PDF-aware attachments** — uploaded decks and documents have their text
  extracted so a run executes on content, not metadata.

### Templates
- **37 built-in templates** across six groups — build, debug your company,
  debug your life, enterprise, debug the agent, govern the agent — three
  starred by default for a first run.
- **Repeat-shape suggestion** — run the same loop shape three times and
  NodeXLoop offers to save it as a template or submit it to your org.

### Organizations *(3.8)*
A loop that already works is worth more than documentation, so the unit of
sharing is a whole reviewed graph — and the point is that somebody read it.

- **Real accounts.** A username and a password, not a typed display name.
  The display name is what approvals and forks are attributed to; it is
  deliberately not the credential. Disabling an account invalidates the
  session it is already holding, not just the next one.
- **Employee enrollment keys.** An admin mints one per person — labelled,
  use-capped, expiring, revocable, and attributed to whoever redeems it. A
  new organization joins by key only. Keys and admin codes are stored
  hashed and shown exactly once.
- **Everything above is in the Orgs tab**, and there is a terminal admin
  console (`nxl-admin`) for the same calls — mint, list and revoke keys,
  manage accounts, rotate the admin code — which is the better tool when
  the batch is twenty people rather than one. It ships to org admins and is
  not published on this repo yet; open an issue if you want it sooner.
- **Review pipeline with separation of duties** *(3.8.3)* — submit →
  sandbox → approved → released, every transition attributed. The submitter
  **cannot approve or release their own graph**; a different account must,
  keyed on the unique username rather than the display name. Nothing
  becomes loadable without a named human on it.
- **Device-only mode is still there**, with no account and no server, for
  solo or offline work — and the app says which mode you are in wherever it
  matters.

### Flow — fork a loop, watch the team *(3.8)*
The part of git worth copying, for loops.

- **Fork without touching the original.** Copy-on-write branches off a
  teammate's graph; the parent is never written to, which is the whole
  guarantee.
- **One attributed activity log per project**, rendered as chat — a colour
  per person, an icon per action, click a row to expand its detail. Forks,
  edits, runs and submissions all land in the same stream, and runs
  auto-log with the governor's savings.
- **Visibility is enforced server-side**, not by the view: you see a
  project only if you are attached to it.
- **Live collaboration rooms** — share a graph as a room link and edit it
  together, with graph sync, presence and peer cursors. A room link is the
  whole capability, Drive-share style. (Browser app; the extension points
  you there, because its webview blocks the outbound socket.)

Model API keys never leave your machine on any of these paths — the graph
that gets shared is key-free, and the server refuses a payload carrying one.

### Evidence
- **Audit report export per run** — provenance, cost, every governance
  decision, and the full log in one print-ready document; estimated figures
  are labelled as estimates.
- **Locally sealed run manifests** — tamper-evident on your machine, and
  claiming nothing more than that.
- **Fleet governance sandbox** — a 1–12 robot dispatch/charging sandbox for
  exercising authority gates against a moving system.
- **A Get-started tab** — three steps to a first run and the handful of
  things the canvas doesn't make obvious.

## Install

| Channel | How |
|---|---|
| **VS Code Marketplace** | [NodeXLoop](https://marketplace.visualstudio.com/items?itemName=orivael.loop-graph-engineer) — or search "NodeXLoop" in the Extensions view |
| **Open VSX** (VSCodium, Cursor, Gitpod) | [orivael/loop-graph-engineer](https://open-vsx.org/extension/orivael/loop-graph-engineer) |
| **Direct `.vsix`** | [Releases](https://github.com/Orivael-Dev/nodexloop/releases/latest) — then VS Code → Extensions → `···` → *Install from VSIX*. Each release lists its SHA-256. |
| **Browser, no install** | [nodexloop.orivael.dev](https://nodexloop.orivael.dev) — sim mode runs whole loops offline, no account, no API key |
| **Browser + a real IDE** *(experimental)* | [ide.orivael.dev](https://ide.orivael.dev) — editor, terminal, Python and git alongside the canvas. Access by request; see [Experimental builds](#experimental-builds). |

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

### NodeXLoop with an IDE — [ide.orivael.dev](https://ide.orivael.dev) *(experimental)*

The whole product in a browser tab: the canvas and the guard alongside a
real editor, a real terminal, and Python, pip and git — so a Module
Resolver install actually installs, and a Run node actually runs. It is a
distribution of [openvscode-server](https://github.com/gitpod-io/openvscode-server)
(Code-OSS, MIT) with the extension baked in; no Microsoft marketplace or
branding is involved.

**Access is by request** — the link is behind HTTP basic auth and will
return 401 without credentials. It is an early build we are testing with a
small number of people rather than an open service, and saying so is more
useful than a login page that pretends otherwise. Open an issue if you want
in.

Not the same thing as [nodexloop.orivael.dev](https://nodexloop.orivael.dev),
which is the app alone — open, no account, no sign-in, and no terminal
behind it.

## Privacy

The guard classifies in-process — prompts are not sent anywhere for
checking. In live mode your prompts go only to the model provider you
configured. Locally sealed run manifests are tamper-evident on your
machine; they do not claim more than that.

## License

[Apache-2.0](LICENSE).
