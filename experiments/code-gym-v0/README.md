# NodeXLoop Code Gym v0: local vs NIM

An **experimental, standalone** model comparison harness, committed alongside an importable NodeXLoop graph. The public NodeXLoop repo currently contains templates and docs, not the extension runtime. The graph is an editable visual companion; the Python runner **does not yet invoke NodeXLoop's graph runtime or AXIOM Guard**.

## Question

Can a smaller coding model recover from short programming errors using sandbox feedback or NIM-model critiques, and how close does it get to a stronger NIM model on independently graded tasks?

| Condition | First answer | Repair behavior |
|---|---|---|
| small_direct | small | none |
| large_direct | NIM | none |
| small_gym | small | up to two repairs from visible deterministic checks |
| small_teacher | small | up to two repairs, each preceded by a NIM coaching critique |

For each task and repetition, **the same first small-model answer** is reused for three small-model conditions. This prevents first-attempt sampling differences from confusing their relative repair gains. The NIM direct baseline is sampled independently. Reported per-condition model latency/tokens include the shared initial call as a counterfactual; **do not sum the rows to estimate the actual API bill**.

Ten deliberately broken, synthetic Python tasks are in tasks.json. Visible tests may be used for coaching; the held-out cases are never provided in prompts. This is a discovery experiment, not a standardized benchmark or evidence of weight changes.

## Install and validate

Requires Python 3.10+, PyYAML, Docker, and a local OpenAI-compatible model plus a large-model NIM/OpenAI-compatible endpoint.

    python -m pip install -r experiments/code-gym-v0/requirements.txt
    python experiments/code-gym-v0/run_gym.py --check
    python -m unittest discover -s experiments/code-gym-v0/tests -v

Pre-pull the sandbox image **yourself** before running (the grading command uses Docker \`--pull=never\`):

    docker pull python:3.12-alpine

For production reproducibility, replace the mutable image tag with an approved SHA-256 image digest.

## Configure endpoints

The runner deliberately reads credentials **only from environment variables**, never YAML or Git.

    export SMALL_BASE_URL="http://127.0.0.1:11434/v1"
    export SMALL_MODEL="<local-model-id>"
    export SMALL_API_KEY=""               # local servers may not require a key

    export LARGE_BASE_URL="https://integrate.api.nvidia.com/v1"
    export LARGE_MODEL="<NIM-available-model-id>"
    export LARGE_API_KEY="<NVIDIA-API-KEY>"

NVIDIA-hosted endpoints and self-hosted NIM endpoints can differ: set the exact base URL/model returned by your provider. Ollama's OpenAI-compatible endpoint is one option for the small model. No credentials or calls are made by \`--check\`.

## Run

One-task smoke benchmark (four conditions, one repeat):

    python experiments/code-gym-v0/run_gym.py --limit 1 --repeats 1

All ten tasks with three repetitions (default):

    python experiments/code-gym-v0/run_gym.py

Reports are saved to ignored \`results/gym-<UTC>.json\`: raw candidate outputs, visible + hidden case counts, per-attempt feedback, model IDs, latency, and token usage when providers report it. Summaries include first-pass rate, final hidden pass rate, and mean fraction of hidden tests passed. Results are **not** automatic model-training examples until reviewed, deduplicated and checked for data leakage. Do not commit production customer code or credentials to fixtures/results.

## Safety and limitations

- Candidate Python is executed **only inside ephemeral Docker containers**: network disabled, read-only root, dropped capabilities, no-new-privileges, non-root UID, CPU/memory/PID limits, Python CPU limit, and a subprocess timeout. The Docker daemon itself must be trusted; use a disposable isolated host for untrusted models.
- This is a practical sandbox, **not a formally hardened defense against malicious code**. Hidden checks run alongside candidate code and could be attacked by a deliberately adversarial submission. Production-grade benchmark integrity needs separate grader isolation and tamper detection.
- Neither AXIOM Guard nor CAS is currently wired into this runner. Do not interpret the manifest's governance note or the companion graph as live enforcement.
- No runtime model calls were executed just by adding this experiment. A NIM key, model endpoints, and a local Docker installation are required for actual comparison results.
- Because a repair is stopped once **visible** tests pass, some agents can still fail hidden cases. This is intentional, and quantifies whether visible-test feedback generalizes.
- Teacher critique adds extra model time/tokens. Compare correctness **and** cost, not just the score.
- Repeating the same ten synthetic tasks three times does not create a statistically representative code benchmark. Use larger, independently sourced held-out tasks before making external performance claims.

## Future integration

Connect \`GymExperiment\` to the NodeXLoop canvas, AXIOM/CAS permission evaluations, versioned training trajectory export (SFT/preference/RL), stronger sandboxed grading, and larger held-out task suites. None of those capabilities are asserted as present in v0.
