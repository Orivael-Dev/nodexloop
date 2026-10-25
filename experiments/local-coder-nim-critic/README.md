# Local coder + NVIDIA NIM critic, for scripts and Git bugs

The **importable NodeXLoop visual template** is [../../templates/local-coder-nim-critic.loop.yaml](../../templates/local-coder-nim-critic.loop.yaml). In the NodeXLoop editor, assign a local Ollama/llama-server model to the *Local coding model* node and your NIM model to the *NVIDIA NIM code critic* node. The public NodeXLoop repository does not contain extension runtime source; importing the YAML provides the workflow shape but does **not** automatically run shell commands, choose models, or enforce a test gate.

This directory provides an executable **separate runner** for the same roles:

\`\`\`text
 Git HEAD snapshot -> local coder -> Docker unittest -> NIM critic
                                  ^                  |
                                  +---- corrections--+
                  -> proposed .patch + JSON history (original repo untouched)
\`\`\`

Two modes share the same loop:
- **debug**: replace one authorized existing Python file to repair a test failure
- **create**: author one explicitly permitted new Python script

Model-generated source is syntax-checked on the host, **never executed on the host**, and then tested inside an ephemeral Docker container with no network, read-only filesystem, non-root user and resource constraints. An NIM review does not override failing tests. Up to three attempts. Output is a candidate patch and trajectory for **human review**, never an automatic write/commit/PR.

## Prerequisites

Python 3.10+, Git, Docker, PyYAML, local OpenAI-compatible coding endpoint, a NIM/OpenAI-compatible critic endpoint. Reuses the previous experiment's hardened HTTP transport in \`../code-gym-v0/run_gym.py\`.

\`\`\`bash
python -m pip install -r experiments/code-gym-v0/requirements.txt
docker pull python:3.12-alpine

export SMALL_BASE_URL="http://127.0.0.1:5000/v1"
export SMALL_MODEL="my_model"
export LARGE_BASE_URL="https://integrate.api.nvidia.com/v1"
export LARGE_MODEL="nvidia/nemotron-3.5-super-vl-120b-a12b"
export LARGE_API_KEY="<NIM key in environment, not YAML>"
\`\`\`

Substitute actual supported model IDs. The NIM vision-language model can act as critic, though a code-focused NIM may be a better controlled comparison.

## Run the DEBUG exercise on this Git repository

Use a **clean checkout** with this branch's fixture committed locally:

\`\`\`bash
python experiments/local-coder-nim-critic/run_workbench.py \
  --repo . --mode debug \
  --file experiments/local-coder-nim-critic/fixtures/debug/checkout.py \
  --task "Repair discount rounding using exact integer cents; preserve the existing function API and pass all checkout tests" \
  --test "python -m unittest discover -s experiments/local-coder-nim-critic/fixtures/debug -p test_*.py -v"
\`\`\`

## Run the CREATE exercise

The intended script does not exist yet, but its tests do:

\`\`\`bash
python experiments/local-coder-nim-critic/run_workbench.py \
  --repo . --mode create \
  --file experiments/local-coder-nim-critic/fixtures/create/tag_tools.py \
  --task "Implement normalize_tag(text) retaining lowercase ASCII letters/digits and merging separator runs to hyphens" \
  --test "python -m unittest discover -s experiments/local-coder-nim-critic/fixtures/create -p test_*.py -v"
\`\`\`

The tests are intentionally visible to the sandbox, but **are not sent to the models**. The coder receives the task and original authorized target file, the critic receives the task, diff, candidate file and actual test results. This is a hands-on debugging exercise, not a held-out benchmark.

Output: \`results/run-<UTC>.json\` and matching \`.patch\`, ignored by Git. Inspect manually; **the original working tree is unchanged**. If you want the candidate in a separate scratch Git worktree, apply it there after review, e.g. \`git apply --check /path/to/run.patch\`. The \`create\` patch is a proposed file creation and may need inspection before application.

## Using another Git repo

- Supply \`--repo /path/to/clean/check-out\` and an explicit \`--file relative/path.py\`. The target is the **only file the model may replace**.
- \`git archive HEAD\` copies committed files into a disposable temporary directory, so outstanding working-tree changes are rejected. No remote Git fetch/push, hooks, npm or pip installs.
- Supply a safe \`python -m unittest ...\` acceptance command. Commands are argument parsed and executed only in a networkless Docker sandbox, not a shell.
- The local model and NIM critic **receive the task and relevant selected code/diffs/test output**. Treat any submitted proprietary code, paths, or test failure text as information going to the model endpoints you configured. Use a synthetic or sanitized repository until data-sharing and permission policies are settled.
- The Docker snapshot includes *tracked* repo files, and its sandbox is not a formally hardened security boundary. Use a disposable VM when code is untrusted, and audit the repo for tracked secrets beforehand.

## Next steps

Integrate the same roles with NodeXLoop's real extension runtime, Axiom/CAS authority enforcement, and strict model binding when runtime source is available. The current runner does **not** use NodeXLoop's in-process guard. Critic comments and success labels should not be treated as training data without independent review.
