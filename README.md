# KCG — University of Galway / Ollscoil na Gaillimhe / Kings College Galway

> **Wordplay (canonical):** *Kings College Galway* is the historical
> English name for the institution now called *Ollscoil na Gaillimhe*
> / *University of Galway* (renamed 2022). The repo preserves the
> original English name as a deliberate backwards-compatibility alias
> — many alumni documents + council minutes still reference the
> Kings College Galway nomenclature.
>
> **GitHub location:** https://github.com/cianfhoghlaim/ollscoil-na-gaillimhe
> (the Irish name for UoG was chosen over `kings_college_galway`
> because that GitHub repo URL is already taken by the original
> cianfhoghlaim monorepo pre-rename). The local working directory
> remains `~/dev/kings_college_galway/` for backwards compatibility.
>
> **Scope (per `LICENSE.md`):** OSINT-only public-document processing
> for the University of Galway. **Strictly restricted** to public-
> facing documents published by the University of Galway, its
> constituent colleges, faculties, schools, research centres, and the
> Students' Union (USG / Comhaltas na Mac Léinn). Ingestion of student-
> private documents (coursework, grades, fees) is explicitly out of
> scope.

This repo is the canonical home for the **University of Galway
document processing pipeline**: ingest public UoG documents (academic
calendar, course catalog, governance minutes, press releases,
research outputs) → BAML extraction → CocoIndex embedding → semantic
search + per-persona marimo dashboards.

## What this repo IS

- A sibling repo to `~/dev/ciandlithe` (civil litigation) + `~/dev/cianchosaint` (defence / policing / intel oversight) + `~/dev/cianfhoghlaim` (main monorepo)
- The canonical DLT + BAML + CocoIndex pipeline for UoG public documents
- The staging ground for the SU agents in `~/dev/ciandlithe/agents/adk/students_union/` to consume real-world UoG data

## What this repo IS NOT

- A platform for student-private documents (coursework, grades, fees) — out of scope
- A replacement for the actual UoG systems (SLS, Banner, etc.) — read-only mirror
- A platform for academic research collaboration — use `~/dev/cianfhoghlaim` for that

## Routing table — "where do I do X in kcg?"

| I want to... | Look at... |
|:--|:--|
| Add a new DLT source for a UoG public surface | `dlt_sources/uog/<surface>.py` — mirror the existing `academic_calendar.py` pattern |
| Add a new BAML extraction function | `baml_src/uog/processing/<domain>.baml` |
| Add a new CocoIndex embedding flow | `cocoindex_flows/uog/<domain>_flow.py` — mirror the existing `courses_flow.py` pattern |
| Add a new per-persona notebook | `notebooks/<notebook_name>.py` — marimo with PEP 723 inline deps |
| Run the openspec validation gate | `openspec validate <change-id> --strict` |
| Wire the SU agents to consume UoG data | `~/dev/ciandlithe/agents/adk/students_union/` (cross-repo reference) |

## Cross-repo convention

KCG is a sibling repo to `~/dev/ciandlithe`. The two repos share:

- The openspec workflow (same `openspec/` layout, same `spec-driven` schema)
- The dlt + BAML + CocoIndex pipeline convention (same patterns)
- The marimo notebook convention (PEP 723 inline deps + `@app.cell` layout)
- The Infisical `dev-baile` vault (kcg lives in its own `kcg/` folder)
- The MotherDuck + LanceDB stack (kcg uses the `md:kcg` database namespace)

The two repos diverge on:

- Domain (civil litigation vs University of Galway public docs)
- Licence (Ciandlithe: court-facing procedural rules; KCG: public UoG documents)
- Persona surfaces (Ciandlithe: civil-litigation analysts; KCG: UoG staff + SU + students)

## Quickstart

```bash
cd ~/dev/kings_college_galway

# Bootstrap the dev environment
uv sync

# Run the doc processing smoke test
python3 scripts/smoke_test.py

# Run the marimo notebook
marimo edit notebooks/uog_doc_processing_pipeline.py

# Validate the openspec change
openspec validate kcg-university-of-galway-doc-processing-v1 --strict
```

## DO NOT

- Ingest student-private documents (coursework, grades, fees). The DLT
  source layer MUST refuse to add a non-public URL.
- Use this repo to scrape protected/sensitive UoG systems (Banner, SLS,
  library databases). The OSINT allowlist IS the licence ceiling.
- Commit the marimo `__marimo__/` cache or the `stedding/` site_scrape_samples.
  Both are gitignored.
