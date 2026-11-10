# Claude Skills

Skills are folders of instructions that teach Claude how to do a specific task the way this project wants it done.

## How to add a skill
1. Copy `_template/` to a new folder, e.g. `streamlit-page/`.
2. Edit its `SKILL.md`: give it a name, a description of when to use it, and the steps.

## Installed skills
All three were installed with `npx skills add` and are recorded in `skills-lock.json`.

| Skill | Source | Use it for |
|-------|--------|-----------|
| `developing-with-streamlit` | [streamlit/agent-skills](https://github.com/streamlit/agent-skills) | Building, styling, caching and deploying Streamlit apps (needs Streamlit 1.57+) |
| `supabase-postgres-best-practices` | [supabase/agent-skills](https://github.com/supabase/agent-skills) | Tables, migrations, RLS policies, indexes and functions (all work in `supabase/`) |
| `ui-ux-pro-max` | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | Styles, palettes, fonts, accessibility and design systems |

Install commands (from the project folder):
```bash
npx skills add https://github.com/streamlit/agent-skills --skill developing-with-streamlit
npx skills add https://github.com/supabase/agent-skills --skill supabase-postgres-best-practices
npx skills add https://github.com/nextlevelbuilder/ui-ux-pro-max-skill --skill ui-ux-pro-max
```
Start a new Claude Code session afterwards so it picks them up.

**Safety review (done on 2026-11-09):** None of the skill scripts download files or call the internet. `developing-with-streamlit` runs one script that finds where Streamlit is installed. `supabase-postgres-best-practices` is Markdown only. `ui-ux-pro-max` searches its own local data files; its only delete is its own temporary file, and it writes design-system files only when asked to save them. Review again after any update.

## Skill ideas for this project
| Skill | Purpose |
|-------|---------|
| `streamlit-page` | How to create a new store page consistently |
| `supabase-migration` | How to write and review database migrations safely |
| `product-catalog` | Rules for product names, prices, and images |
| `deploy` | Steps to deploy the app |
