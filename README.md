# 🥔 Potato Chip Store

A demo online store where shoppers build their own bag of chips: pick a base chip, then add 1–3 flavors. It's built as a training project for learning to make a real-world app with Streamlit, Supabase and GitHub.

> **Status:** Foundation built: database, sign-in, app shell with every screen as a "Coming soon" page, tests. Stories are next.
> **Demo only:** No real payments, no real emails, fictional data.

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| App | [Streamlit](https://streamlit.io) (Python 3.11+) | Storefront, cart, checkout and admin screens |
| Backend | [Supabase](https://supabase.com) | Postgres database, sign-in, product image storage |
| Hosting | [Streamlit Community Cloud](https://streamlit.io/cloud) | Recommended; see [ADR 0001](docs/architecture/decisions/0001-hosting-platform.md) |
| Collaboration | GitHub | Issues, pull requests, Actions (CI) |

## Start Here

1. [docs/requirements/00-consolidated-requirements.md](docs/requirements/00-consolidated-requirements.md): what we're building
2. [docs/planning/work-division-plan.md](docs/planning/work-division-plan.md): who builds what, and how we use GitHub

## Repository Structure

```
potato-chip-store/
├── README.md                  ← You are here
├── CLAUDE.md                  ← Project context and rules for Claude Code
├── requirements.txt           ← Python packages
├── skills-lock.json           ← Agent skills installed with `npx skills add`
├── .env.example               ← Copy to .env (never commit .env)
├── .gitignore
│
├── .streamlit/
│   ├── config.toml            ← Theme and settings
│   └── secrets.toml.example   ← Copy to secrets.toml (never commit it)
│
├── .claude/
│   ├── skills/                ← Agent skills (Streamlit, Supabase, UI/UX)
│   └── hooks/                 ← Docs for automated checks
│
├── app/                       ← Streamlit application
│   ├── pages/                 ← One file per screen (S1–S16)
│   ├── components/            ← Reusable UI pieces (product card, flavor tile…)
│   ├── services/              ← All Supabase calls (catalog, cart, orders, admin, auth)
│   ├── models/                ← Data classes (BaseChip, Flavor, Bag, Order…)
│   ├── utils/                 ← Helpers (pricing, guards, session, outbox)
│   └── config/                ← Loads settings and secrets
│
├── assets/
│   ├── images/                ← Logos and product images
│   └── styles/                ← Custom CSS (keep it small)
│
├── docs/
│   ├── requirements/          ← 00 summary, 01 stories, 02 UI/UX, 03 non-functional
│   ├── planning/              ← Work division plan, personas, story map, backlog
│   ├── architecture/          ← Architecture, data model, ADRs (decisions/)
│   ├── deployment/            ← How to deploy (Streamlit Community Cloud)
│   └── design/                ← Wireframes and mockups
│
├── supabase/
│   ├── migrations/            ← SQL schema migrations (RLS on every table)
│   └── seed/                  ← Demo data
│
├── tests/
│   ├── unit/                  ← Fast tests, no database
│   └── integration/           ← Tests against a local Supabase
│
└── scripts/                   ← Helper scripts (seed users, create issues…)
```

Empty folders contain a `.gitkeep` file so Git keeps them.

## Getting Started (Windows)

Type these in **PowerShell**. Lines starting with `#` are notes, not commands.

### 0. Install once
- **Python 3.11 or newer** from [python.org](https://www.python.org/downloads/). On the first installer screen, tick **"Add python.exe to PATH"**.
- **Git** from [git-scm.com](https://git-scm.com/download/win).
- **VS Code** and the **Claude Code** extension (for the class).

Check they work (each prints a version):
```powershell
py --version
git --version
```

### 1. Clone the repo
```powershell
cd $HOME\Documents
git clone https://github.com/zandertran10/potato-chip-store.git
cd potato-chip-store
```

### 2. Create and turn on a virtual environment
A virtual environment keeps this project's packages separate from everything else.
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```
Your prompt now starts with `(.venv)`. Do step 2's second line every time you open a new terminal.

If PowerShell says *"running scripts is disabled on this system"*, run this once, then try again:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 3. Install the packages
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Add the Supabase keys (`.env`)
```powershell
copy .env.example .env
code .env
```
Fill in the two values the Tech Lead sends you privately, then save:
```
SUPABASE_URL=https://<your-project>.supabase.co
SUPABASE_PUBLISHABLE_KEY=<the sb_publishable_... key>
```
- Use the **publishable** key only (Supabase → your project → Connect, or Project Settings → API Keys). The app refuses a **secret** key (`sb_secret_...`, formerly `service_role`).
- An older `.env` that says `SUPABASE_ANON_KEY=` still works.
- `.env` is gitignored. **Never commit it, paste it into chat, or screenshot it.**

### 5. Run the app
```powershell
streamlit run app/streamlit_app.py
```
Your browser opens at http://localhost:8501. Stop the app with **Ctrl+C**.
You can click around as a guest without keys. To sign in, use a demo account from the Tech Lead (setup: [docs/deployment/demo-accounts.md](docs/deployment/demo-accounts.md)).

### 6. Run the checks
The same checks run on every pull request (CI):
```powershell
ruff check . --extend-exclude .claude
python -m pytest tests/unit -q
```
Both should pass before you open a pull request. Unit tests use a fake Supabase (`tests/conftest.py`), so they need no keys and no internet.

### Troubleshooting

| You see | Fix |
|---|---|
| "The store isn't set up yet: SUPABASE_URL ... is missing" | Step 4: `.env` is missing or empty |
| `ModuleNotFoundError: No module named 'streamlit'` | The venv isn't on: `.\.venv\Scripts\Activate.ps1` |
| `'streamlit' is not recognized` | Same: turn on the venv, or use `python -m streamlit run app/streamlit_app.py` |
| "Email or password is wrong." with a demo account | Check the password with the Tech Lead; the accounts are made in [demo-accounts.md](docs/deployment/demo-accounts.md) |
| Port 8501 is busy | `streamlit run app/streamlit_app.py --server.port 8502` |

## Database (Tech Lead)

The database lives in Supabase. To set up a new project, apply `supabase/migrations/` in number order, then follow [docs/deployment/demo-accounts.md](docs/deployment/demo-accounts.md) for the sample data and demo accounts. `supabase/tests/place_order_test.sql` checks the order function.
