# Architecture

## Overview
Browser → Streamlit app (Python) → Supabase (Postgres + Auth + Storage)

## Components
- **Streamlit app:**
- **Supabase database:**
- **Supabase Auth:**
- **Supabase Storage:** (product images)
- **Hosting:** see `decisions/0001-hosting-platform.md`

## Environments
| Environment | Purpose | URL |
|-------------|---------|-----|
| Local | Development | |
| Production | Live store | |

## Security notes
- Secrets in environment variables only
- RLS enabled on every table
