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
  change → test → approve, with fifteen node types (agents, critics, gates,
  loops and merges, plus Run, Search, MCP Tool, Module and Swarm),
  drag-and-drop wiring, undo, and graph import/export.
- **Loop Architect** *(4.3)* — describe the loop you want in a sentence and a
  checked draft lands on the canvas, runs in sim, and comes back as the nodes
  talking. The guard reads your words before the model does. A draft is held
  to nine plain node types (no Run, MCP, Search, Swarm or Module), one input,
  at least one output, and cycles only through a critic loop of at most ten
  iterations; a draft that fails is sent back once, then replaced by the
  closest template. It is an ordinary edit, so Undo restores the canvas. With
  no model configured it matches templates offline and spends nothing.
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
- **Agent fleet kill switch** *(4.3)* — *NodeXLoop: Set Agent Fleet Level*
  applies one ladder to every agent run in the workspace. L2 THROTTLE sends
  model calls one at a time and asks before a run node or swarm; L3 SUSPEND
  refuses new ones; L4 TERMINATE aborts every in-flight model call and kills
  every swarm and run node together with everything it started, within
  250 ms. Raising needs no key; lowering is a signed release, and a release
  that doesn't verify reads as L3. Every change is a hash-chained receipt.

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

### Connect it to your tools *(3.9 – 4.2)*
All four are off until you turn them on, and all four go through the guard.

- **Search node** *(3.9)* — loops can search the web through your own SearXNG
  instance (no key), Brave or Tavily (key in the OS keychain, never in the
  graph). Results go downstream marked untrusted. The query is checked before
  it leaves and the results before a model reads them; sim runs and the
  browser build never send a query.
- **MCP Tool node** *(4.2)* — call any tool on any server in your workspace's
  `.mcp.json` (the file Claude Code reads) as a graph step. Arguments are
  guarded before they leave and results before a model reads them; a tool
  that doesn't declare itself read-only asks in a VS Code modal before every
  call. Credentials stay in the OS keychain or environment and never reach the
  webview. stdio and Streamable HTTP; trusted workspaces only; sim runs never
  start a server.
- **Webhooks for n8n, Zapier and Make** *(4.2)* — `run.started`,
  `run.finished`, `guard.blocked`, `loop.stalled`, `submission.released` and
  *(4.3)* `dependency.down` / `dependency.recovered`, HMAC-SHA256-signed when
  you set a secret. A Slack incoming-webhook URL is recognised and sent a short
  Slack message instead of the JSON envelope. `guard.blocked` carries a hash of
  the input, never the blocked text.
- **Autopilot** *(4.2)* — proposes repairs for failed, stalled or
  below-threshold runs from debugging templates you register, only inside
  hourly repair and token budgets, a same-failure cooldown, and a circuit
  breaker that waits for a human after three weak repairs. Repairs are
  simulated, so Autopilot cannot trigger itself; healthy runs are never
  touched.

### The night shift *(4.3)*
For the hours nobody is watching. These run beside the app as small Node 18+
daemons with no npm install. They are not part of the extension download
and are **not published on this repo yet**; open an issue if you want them.

- **Triggers** — start governed loops on a cron schedule or from an n8n /
  Zapier event. A schedule runs live only inside a **mandate**: limits a named
  person signed in advance, bound to the exact loop bytes, endpoint, model,
  run and dollar caps, per-run time limit, and an expiry of at most 90 days.
  An inbound event **never** runs live: it is authenticated, replay-windowed,
  de-duplicated and guarded, then run offline and queued for a person. Every
  decision is sealed into a chained ledger before the run it decides.
- **SilenceWatch** — turns silence into an alert: a job that stopped beating,
  a job that failed, a third-party API that went down or quietly degraded.
  One alert per incident with spaced reminders, a daily canary that proves the
  alert path works, and Slack, email (STARTTLS required) or a signed webhook.
  Alerts carry a host and an error class, never a path, header or body. A
  watcher on the machine it watches dies with it, and the docs say so.
- **The morning brief** — what ran overnight, what is waiting (with the exact
  command to approve each), what failed or was held, and the reported spend,
  delivered to Slack, email or a signed webhook. A quiet night says so, and a
  brief that doesn't arrive is itself an alert.
- **Night-shift pack** — five loops that leave drafts for a person: support
  replies, an inbox digest, invoice reminders, a weekly KPI brief, and replies
  to new leads. **Nothing is ever sent**: every loop ends at an output for
  review, every agent is bounded (steps, tokens, wall time) with no tools and
  no network, and critics check every figure against the input.

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
- **51 built-in templates** across nine groups — build and ship, debug your
  company, debug your life, enterprise operations, debug the agent, govern
  the agent, bootstrapped startup, established SMB & enterprise, and
  outcome-based coding — three starred by default for a first run.
- **Outcome-based coding** *(4.0)* — seven loops for small and mid-sized
  businesses that start from a result the business can name, write down
  their definition of done before anything is built, grade against that
  definition rather than the volume of code, and end at an owner gate:
  outcome to shipped feature, spreadsheet to internal tool, SaaS-to-SaaS
  integration, busywork automation, the owner's numbers report,
  behaviour-preserving modernization, and a release go-live gate.
- **Startup and scale-up groups** *(4.1)* — MVP scope, pricing and packaging,
  first-customer outreach; vendor evaluation, OKR cascades, role onboarding.
  Plus an **evidence-cited prospect finder** whose fit criteria are fixed
  before any search, so the test can't bend toward what was found.
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
- **Real robot simulators on the Fleet map** *(4.1)* — add one from a Hugging
  Face Space and it is pinned to a commit, hash-verified file by file, built
  only after you confirm the exact commands, and run in its own panel behind a
  CSP that denies the network. A running sim appears as a live robot, and the
  same escalation ladder applies to it (L2 slows it, L3 holds it, L4 closes
  it). Every import, build and level change is a sealed receipt. *(4.3)* adds
  bounded mission commands (`go_to`, `stop`, `push`, `get_state`) and a
  research harness for testing whether a checker's feedback helps a local
  model steer the sim; on its frozen evaluation set the supervisor tied plain
  retries, 24 of 40 each, and the write-up records that as *not shown*.
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
agent · govern the agent). 4.3 ships **51**: the 16 added since — the two
community templates below, the seven outcome-based coding loops, the six
startup and scale-up templates, and the prospect finder — are not in the book
yet.

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
