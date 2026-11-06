# Claude Skills

Skills are folders of instructions that teach Claude how to do a specific task the way this project wants it done.

## How to add a skill
1. Copy `_template/` to a new folder, e.g. `streamlit-page/`.
2. Edit its `SKILL.md`: give it a name, a description of when to use it, and the steps.

## Installed skills
| Skill | Source | Purpose |
|-------|--------|---------|
| `developing-with-streamlit` | [streamlit/agent-skills](https://github.com/streamlit/agent-skills) (copied, not modified) | Loads the Streamlit reference docs that match the installed Streamlit version (needs Streamlit 1.57 or newer) |
| `supabase-postgres-best-practices` | [supabase/agent-skills](https://github.com/supabase/agent-skills), installed with `npx skills add` (tracked in `skills-lock.json`) | Postgres rules for tables, migrations, RLS policies, indexes, and functions. Use it for all work in `supabase/` |

To update it, download the latest copy from the source repo and replace the folder.

## Skill ideas for this project
| Skill | Purpose |
|-------|---------|
| `streamlit-page` | How to create a new store page consistently |
| `supabase-migration` | How to write and review database migrations safely |
| `product-catalog` | Rules for product names, prices, and images |
| `deploy` | Steps to deploy the app |
