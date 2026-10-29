# Claude Hooks

Hooks are commands that run automatically at certain points while Claude works (for example, after Claude edits a file). They help keep the project consistent without anyone having to remember.

Hooks are configured in `.claude/settings.json` (to be added later). This folder documents what each hook does and why.

## Planned hooks
| Hook | When it runs | What it does |
|------|-------------|--------------|
| Format Python | After a `.py` file is edited | Runs a code formatter (e.g. `ruff format`) |
| Secret check | Before a commit | Blocks commits that contain API keys |
| Run tests | After code changes | Runs the test suite in `tests/` |

## Adding a hook
1. Describe it in the table above.
2. Add its configuration to `.claude/settings.json`.
