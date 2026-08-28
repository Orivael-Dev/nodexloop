# Community templates (experimental)

Graphs you can **import** into NodeXLoop. Both of these were promoted into the
extension in **3.6.0** and now ship built in, still marked experimental — which
also means they now go through the built-in template suite they had not been
held to when this page was written. The copies here stay importable for anyone
on an older build.

Experimental means the shape is real and runnable and the disclaimers below
still apply in full — treat each one as a starting point to adapt, not a
finished product.

> ## ⚠️ Disclaimer — read this first
>
> These templates orchestrate an AI model. Their output is **draft, unreviewed,
> and can be wrong.** They are tools for a qualified human to review, not a
> substitute for professional judgement.
>
> - **Legal document drafter — this is NOT a legal service and NOT legal
>   advice.** Using it creates no attorney-client relationship. Anything it
>   produces is an AI-generated draft that may be incorrect, incomplete, or
>   inappropriate for your matter or jurisdiction. **Always have any legal
>   document reviewed by a lawyer licensed in the relevant jurisdiction before
>   you rely on it, send it, or file it.**
> - **Driver update & hardening loop — for review only.** It produces a draft
>   change and never installs anything. AI-generated driver code can be unsafe;
>   never load it onto production hardware. Build and test it in isolation and
>   have a qualified engineer review and sign off before any install.
>
> The same disclaimer travels inside each graph's input node, so it's visible on
> the canvas and in every run. No warranty of any kind — use at your own risk.

## How to import

- **VS Code extension** — open the NodeXLoop panel, `···` → **Import .loop.yaml**,
  and pick the `.loop.yaml` file. The graph lands on the canvas and (in a repo)
  round-trips back to the file.
- **Web app** ([nodexloop.orivael.dev](https://nodexloop.orivael.dev)) — `···` →
  **Import graph JSON**, and pick the `.graph.json` file.

Every node is model-free on import, so each one resolves to *your* default model.
Some nodes expect uploaded files (client documents, precedents, a rules
checklist) — attach those in each node's inspector after importing.

---

## Legal document drafter

`legal-document-drafter.loop.yaml` · `legal-document-drafter.graph.json`

**Not a legal service — see the disclaimer above.** Research → merge → draft →
check skeleton pointed at legal drafting, with an adversarial fact-check turned
into a citation/compliance/risk review, and a human sign-off gate at the end.

```
Matter brief ─┬─► Matter intake ──┬─► Case-law researcher ──┐
              │                   └─► Firm-knowledge ────────┤
              └─► Precedent library ─────────────────────────┴─► Cross-reference ─► Document drafter ─► Citation validator ─┐
                                                                                        ▲                    │             │
                                                                   revise / strengthen /│ fix compliance     │             │
                                                                Final sign-off ◄─ Risk analyzer ◄─ Compliance reviewer ◄────┘
                                                                     │ approved
                                                                     ▼
                                                              Final legal document
```

- **Intake never invents a fact** — a missing value goes on a `MISSING FACTS`
  list rather than being guessed, and the drafter can only cite from the
  case-law researcher's sourced list (anything else gets a `[FACT NEEDED]` /
  `[AUTHORITY NEEDED]` marker).
- **Three review lanes, each looping back to the drafter** — a citation
  validator that treats every citation as fabricated until matched, a compliance
  reviewer for forum rules, and a risk analyzer that reads as opposing counsel.
- **Nothing is "final" without a person** — the sign-off gate is the only path
  to the output.

The risk analyzer carries `adversary: true`, so the guard's HARM preflight
doesn't false-positive on its opposing-counsel prompt while a real injection is
still caught.

## Driver update & hardening loop

`driver-update-hardening.loop.yaml` · `driver-update-hardening.graph.json`

**For review only — see the disclaimer above.** Checks whether a device or
adapter driver is out of date **or** carries a known advisory, and only then
calls a code agent to produce a fix — reviewed for both correctness and security
before a human signs off.

```
Driver target ─┬─► Version inspector ──┐
               └─► Upstream + advisory ─┴─► Staleness diff ─► Out of date / vulnerable?
                                                                    │            │
                                            already current & clean │            │ out of date / vulnerable
                                                                    ▼            ▼
                                                                 (output) ◄── Driver author ◄────┐
                                                                    ▲            │               │
                                                        approved    │           ▼               │ revise / patch / rework
                                                          Install sign-off ◄─ Vuln scanner ◄─ Correctness reviewer
```

- **The check is two lanes that must agree** — a newer version exists, *or* the
  installed one has an advisory. A gate short-circuits to the output when the
  driver is current and clean, so the code agent only runs when there's real work.
- **Two critics on the loop** — a correctness reviewer (does it still do its
  job?) and a vulnerability scanner that assumes the driver is unsafe until the
  diff proves otherwise and checks the original CVE is closed, not moved.
- **Nothing installs without a person.** The output is a *reviewed draft* held at
  a human sign-off gate — a signed diff plus build and advisory evidence.

Turn the Axiom guard on and its loop governor will stop the author/critic cycle
if the diffs stop changing. For a real vulnerability backend rather than an LLM
critic, the scanner node is where the `axiom_shield` / `axiom_cas` MCP tools
would wire in.
